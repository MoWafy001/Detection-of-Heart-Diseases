import pickle

disease_model_path = 'prediction_models/Disease_model.sav'
disease_model = pickle.load(open(disease_model_path, 'rb'))

parentage_model_path = 'prediction_models/Parentage_model.sav'
parentage_model = pickle.load(open(parentage_model_path, 'rb'))

def predict_disease(args):
    return int(disease_model.predict([args])[0])

def predict_percentage(args):
    return int(parentage_model.predict([args])[0])