# Model Manager

Utility app for managing Keras models records and associated files

## API

#### functional API
here are some methods used to interact with saved data

   - _show_all_models_ 
   
   - _show_models_with_tag_ (tag : str) 
   
   - _dump_models_to_df_ 
   
   - _get_history_ (kmodel : KModel instance)
   
   - _plot_history_many_ (in_models : [] , lateral_compare : bool, ignore_none : bool)
        in_models : list of any combinations of str or db kmodel instance  
    lateral_compare : bool, whether the plots will be grouped by models or metrics   
    ignore_none : bool, whether to ignore models that don't have a history artifact  
    return : (a matplotlib figure obj, data dict)  

#### KModel 
inherits from django.db.Model  

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
    
    
#### Artifact
inherits from django.db.Model  
This class is meant to be a record of pickled python objects 
such as model outputs, custom loss functions or Keras model factories.  
Note : artifact couldn't easily modified once created, this will be fixed in the future.  

additional methods : 
    - _payload_ @property this property returns pickled object, 
    multiple calls of this method on the same object 
    will not result in multiple loads.

#### RecorderCallback 
inherents from keras.callbacks.Callback
    

## How Does this work? 

Here is a [Jupyter Notebook Demo](https://colab.research.google.com/drive/17x4ha7EQrOxWcnrKXkRyOV0o-gsfHyWP#scrollTo=sHk62RwlPORa)
hosted on Google Colab

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
