# YooperNet
Software module for handling data from the YooperNet stations.

## Installation
Nothing fancy at this point- just download the folder and add it to
your Python path:

```
# In BASH:
export PYTHONPATH=$PYTHONPATH:/home/yourlocation/YooperNet
```

## Example Usage
Simply import and use the `YooperData` class to open HDF5 files.

```
import YooperNet
data = YooperNet.YooperData('some_example_file.h5')

# Access key variables through dictionary-like syntax:
print(data['b'])
```

## Future Dev
Eventually, this package will depend on Spacepy for visualization
shortcuts and coordinate transforms.
