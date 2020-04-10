# Model Manager

Utility app for managing Keras models records and associated files

## API

#### KModel 
inherents from django.db.Model  

additional methods :    
   - _add_note_ (note : string) this method appends notes to kmodel_instance.notes along with a time stamp   
    
   - _add_tags_ (tags : list) this method accepts a list of tags, str or Tag model instance.
    then adds a many-to-many relationship from self to the Tag obj
    
   - _remove_tags_ (tags : list) this method accepts a list of tags, str or Tag model instance.
    then removes the many-to-many relationship from self to the Tag obj but not the Tag itself
    
   - _add_artifact_ (artifact : arbitrary python obj, descriptor : str, plot : bool)
    descriptor is a string describing the type of data this artifact contains, does not have to be unqiue  
    dumps artifact obj into pickle, create db record,
    returns django model instance
    if plot is true and a pyplot.plot object is passed as artifact, 
    a png of the plot would be saved instead of pickle
    
#### RecorderCallback 
inherents from keras.callbacks.Callback
    

## How Does this work? 

#### Saving model 
Save the model and training history by passing a instance of RecorderCallback to fit or fit_generator

#### Saving data associated with models
call call KModel.add_artifact with arbitrary python object and it will be dumped in to a pickle file  
and an Artifact object instance will be save to db and returned
the path to the pickle file is saved as an attribute to the Artifact object

#### Interacting with database record 
query the database by using Django Queryset API


###_Work In Progress_ 
Stay tuned! 
