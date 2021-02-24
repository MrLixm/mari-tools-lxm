"""

Author: Liam Collod
Last Modified: 24/02/2021

[Support]
    Python 2.7+
    Mari SCRIPT
    Tested on Mari 4.7.v1.

[What]
    Create quickly multiple channels nodes.

[How]
    - Read the INSTRUCTIONS docstring under.

[License]
    This work is licensed under the Creative Commons Attribution-ShareAlike
    4.0 International License.

    To view a copy of this license,
    visit http://creativecommons.org/licenses/by-sa/4.0/

    This license allows reusers to distribute, remix, adapt, and build upon
    the material in any medium or format, so long as attribution is given to
    the creator. The license allows for commercial use. If you remix, adapt,
    or build upon the material, you must license the modified material
    under identical terms.

"""

import mari

_VERSION = '1.0.0'

""" --INSTRUCTIONS---------------------
Modify the bottom 2 variables 

RESOLUTION is the resolution in pixels gave to the created channels
CHANNEL_DATA is the dictionnary of channels to create, 
    'channel_name':
        [0]: bitdepth,
        [1]: is the channel scalar ?
    each line has to end with a , 
    
"""


RESOLUTION = 4096

# channel_name: [bitdepth, is_scalar]
CHANNEL_DATA = {
    'Diffuse_Color': [16, False],
    'Specular_Roughness': [16, True],
    'Specular_Weight': [16, True],
    'Metalness': [16, True],
    'Normal': [16, True],
    'Displacement': [32, True],
}


# ----------------------------------

class ChannelCreator:
    def __init__(self, resolution, channels_data):
        """

        Args:
            resolution(int):
            channels_data(dict):
                { channel_name(str): [bitdepth(int), is_scalar(bool)] }
        """
        self.nodegraph = mari.geo.current().nodeGraph()
        self.resolution = resolution
        self.channels_data = channels_data

    def setup(self):
        color_config = mari.ocio.currentColorspaceConfig()

        for chan_name, chan_data in self.channels_data.items():
            c_bitdepth = chan_data[0]
            c_scalar = chan_data[1]
            self.create_channel(bitdepth=c_bitdepth,
                                color_config=color_config,
                                create_scalar=c_scalar,
                                chan_name=chan_name)

    def create_channel(self, bitdepth, color_config, create_scalar, chan_name):
        """

        Args:
            color_config(mari.ColorConfig):
            bitdepth(int): 8,16,32
            create_scalar(bool):
            chan_name(str):

        Returns:

        """
        try:
            new_channel_n = self.nodegraph.createChannelNode(
                self.resolution,
                self.resolution,
                bitdepth,
                ColorConfig=color_config,
                Name=chan_name)

        except Exception as e:
            _message = 'Cannot create the channel {} : {}'.format(chan_name, e)
            mari.utils.messageAndLog(_message, title='ERROR', log=False)
            return False

        new_channel = new_channel_n.channel()

        # color config
        colconfig = new_channel.colorspaceConfig()
        if create_scalar:
            colconfig.setScalar(True)
            colconfig.setRaw(False)
        else:
            colconfig.setScalar(False)
            colconfig.setRaw(False)
        colconfig.setAutomaticColorspace(colconfig.COLORSPACE_STAGE_NATIVE,
                                         'ACES - ACEScg')
        new_channel.setColorspaceConfig(colconfig)

        # scalar config (mask data)
        scal_colconfig = new_channel.scalarColorspaceConfig()
        scal_colconfig.setScalar(True)
        scal_colconfig.setRaw(True)
        scal_colconfig.setAutomaticColorspace(
            scal_colconfig.COLORSPACE_STAGE_NATIVE, 'ACES - ACEScg')
        new_channel.setScalarColorspaceConfig(scal_colconfig)

        return True


if __name__ == '__main__':
    ChannelCreator(RESOLUTION, CHANNEL_DATA).setup()
