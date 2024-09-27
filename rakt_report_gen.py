""" 
Steps :
- Given is the inference dataset.
- fit bkt on ct dataset
- for each student prepare the confidence_correctness list.
- Make a loop to use each student id's 10 solutions in Roaster class
- Prepare a singel csv for all 36 students
"""

import pandas as pd
from pyBKT.models import *
from pyBKT.models import Model
import time


def train_bkt():
    model = Model(seed = 42, num_fits = 1, parallel = True)
    model.fetch_dataset('https://raw.githubusercontent.com/CAHLR/pyBKT-examples/master/data/ct.csv', '.')
    start_time = time.time()
    model.fit(data_path = 'ct.csv')
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to train BKT: {elapsed_time}")
    
    training_rmse = model.evaluate(data_path = 'ct.csv')
    training_auc = model.evaluate(data_path = "ct.csv", metric = 'auc')
    print("Training RMSE: %f" % training_rmse)
    print("Training AUC: %f" % training_auc)

    return model

def calculate_kma(confidence_correctness):

    kma_list = []
    
    for i in range(0, len(confidence_correctness)):
        FC = PC = FI = 0
        temp_list = confidence_correctness[:i+1]

        # Calculate counts for each question up to n
        for idx, c_c in enumerate(temp_list):
            if c_c[2] >= 0.7 and c_c[2] < 0.9:
                ans = 0.5
            elif c_c[2] >= 0.9:
                ans = 1
            else:
                ans = 0 
            # ans = c_c[1]
            conf = c_c[0]
            
            if conf == 1:
                conf = 'P'
            elif conf == 2:
                conf = 'C'
            else:
                conf = 'I'
                
            if ans == 1:
                if conf == 'C':
                    FC+=1
                elif conf == 'P':
                    PC+=1
                else:
                    FI+=1
            elif ans == 0.5:
                if conf == 'C':
                    PC+=1
                elif conf == 'P':
                    FC+=1
                else:
                    PC+=1
            else:
                if conf == 'C':
                    FI+=1
                elif conf == 'P':
                    PC+=1
                else:
                    FC+=1
                    
        kma = round((FC - 0.5 * PC - FI) / (FC+PC+FI), 4)
        kma_list.append(kma)

    return kma_list

def calculate_kmb(confidence_correctness):
    kmb_list = []
    
    for i in range(0, len(confidence_correctness)):
        NB = PPB = FPB = POB = FOB = 0
        temp_list = confidence_correctness[:i+1]

        # Calculate counts for each question up to n
        for c_c in temp_list:
            if c_c[2] >= 0.7 and c_c[2] < 0.9:
                ans = 0.5
            elif c_c[2] >= 0.9:
                ans = 1
            else:
                ans = 0 
            # ans = idx[1]
            conf = c_c[0]
            
            if conf == 1:
                conf = 'P'
            elif conf == 2:
                conf = 'C'
            else:
                conf = 'I'
                
                
            if ans == 1:
                if conf == 'C':
                    NB+=1
                elif conf == 'P':
                    PPB+=1
                else:
                    FPB+=1
            elif ans == 0.5:
                if conf == 'C':
                    POB+=1
                elif conf == 'P':
                    NB+=1
                else:
                    PPB+=1
            else:
                if conf == 'C':
                    FOB+=1
                elif conf == 'P':
                    POB+=1
                else:
                    NB+=1
                
        # Calculate KMB
        kmb = round((FOB + 0.5 * (POB - PPB) - FPB) / (FOB + POB + NB + PPB + FPB), 4)
        kmb_list.append(kmb)
    return kmb_list

def calculate_deltas(list_delta):
    deltas = []
    
    for i in range(1, len(list_delta)):
        delta = list_delta[i] - list_delta[i - 1]
        deltas.append(delta)
    
    return deltas

def classify_kma(kmas):
    kma_classes = []
    for k in kmas:
        if k >= -1 and k < -0.25:
            kma_classes.append("LOW")
        elif k >= -0.25 and k < 0.25:
            kma_classes.append("AVERAGE")
        elif k >= 0.25 and k < 0.5:
            kma_classes.append("AVERAGE")
        else:
            kma_classes.append("HIGH")
            
    return kma_classes
    
def classify_kmb(kmbs):
    kmb_classes = []
    for k in kmbs:
        if k >= -1 and k < -0.25:
            kmb_classes.append("PESSIMISTIC")
        elif k >= -0.25 and k < 0.25:
            kmb_classes.append("RANDOM")
        elif k >= 0.25 and k < 0.5:
            kmb_classes.append("OPTIMISTIC")
        else:
            kmb_classes.append("OPTEMISTIC")

def main():
    # Read inference data:
    inference_data = pd.read_csv('./Inference-Data-Sample/student_behaviors_simulated.csv')

    # Train BKT model
    model = train_bkt()
    
    # Calculating KMA and KMB for each student's performance (36 * 10)
    for i in range(1, 37):
        df = inference_data[inference_data['student_id']==i]
        confidence_correctness = list(zip(df['given_confidence'], df['acquired_grade']))
        kma = calculate_kma(confidence_correctness)
        kmb = calculate_kmb(confidence_correctness)

        # Get KMA calssifications
        kma_classes = classify_kma(kma)
                
        # Get KMB calssifications
        kmb_classes = classify_kmb(kmb)
                
        # Get KMA & KMB delta list:
        kma_deltas = calculate_deltas(kma)
        kmb_deltas = calculate_deltas(kmb)
        
        # Initializing Roaster to evaluate student performance
        roster = Roster(students = [f'Student {i}'], skills = 'Plot terminating proper fraction', model = model)
        initial_prob = roster.get_mastery_prob('Plot terminating proper fraction', f'Student {i}')

        # Store mastery list:
        mastery_probs = []
        
        for index, row in df.iterrows(): 
            grade_i = row["grade_class"]
            new_state = roster.update_state('Plot terminating proper fraction', f'Student {i}', grade_i)
            prob = roster.get_mastery_prob('Plot terminating proper fraction', f'Student {i}')
            mastery_probs.append(prob)
            
        # Get mastery changes:
        mastery_deltas = calculate_deltas(mastery_probs)
            
        df['awareness'] = kma
        df['awareness_change'] = kma_deltas
        df['awareness_class'] = kma_classes
        
        df['outlook'] = kmb
        df['outlook_change'] = kmb_deltas
        df['outlook_class'] = kmb_classes
        
        df['initial_mastery'] = initial_prob
        df['mastery'] = mastery_probs
        df['mastery_change'] = mastery_deltas
        
        # Saving each report:
        df.to_csv(f'./RAKT-Reports/report-student{i}.csv')
        

        
    
    
    
    






