import numpy as np
import pandas as pd
import tensorflow as tf

class NN_Model:
    def __init__(self, n_features, training = True):
        self.model = self.generate_model(n_features, training)
    
    def generate_model(self, n_features, training):
        airspace_input = tf.keras.Input(shape=(None, n_features), name='Candidate_Input')
        item_input = tf.keras.Input(shape=(n_features,), name='Prediction_Input')
        
        track_1 = tf.keras.layers.GRU(64, return_sequences= True, name='GRU_Layer_1')(airspace_input)
        track_1 = tf.keras.layers.GRU(32, name='GRU_Layer_2')(track_1)
        
        con_track = tf.keras.layers.Concatenate()([item_input,track_1])
        
        con_track = tf.keras.layers.Dense(64, name='Dense_1')(con_track)
        
        output = tf.keras.layers.Dense(1, name='Output')(con_track)
        
        model = tf.keras.Model([airspace_input,item_input], output)
        
        model.compile(optimizer='adam', loss='mse')
        
        print(model.summary())
        
        return model
        
    def leader_election(self,aircraft, towers, active_idxs, active_towers, sim_time):
        if sim_time %0.25 != 0 or len(active_idxs)==0:
            return
    
        data = [np.zeros(7) for _ in range(len(active_idxs))]

        for i, idx in enumerate(active_idxs):
            d = np.insert(aircraft[idx], 0, [sim_time])
            active_tower = towers.get_parent_tower(aircraft.positions[idx])
            d = np.append(d, [
            active_tower,
            towers.get_parent_tower(aircraft.position_error[idx]),
            len(towers.aircraft_list[active_tower]),
            np.linalg.norm(aircraft.positions[idx] - towers.centres[active_tower]),
            np.linalg.norm(aircraft.position_error[idx] - towers.centres[active_tower])
            ])
            data[i] = d

        data = np.vstack(data)
    
        df = pd.DataFrame(np.array(data), columns=('Tx t','pos.x', 'pos.y', 'err.x', 'err.y', 'vel.x', 'vel.y', 'accel.x', 'accel.y', 'hdg', 'flt time', 'max flt time', 'h(x)', 'active', 'tower', 'err.tower','neighbours','true.dist','err.dist'))