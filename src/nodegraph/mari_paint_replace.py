"""
Author: Liam Collod
Last Modified: 26/02/2021

[Support]
    Python 2.7+
    Mari SCRIPT
    Tested on Mari 4.7.v1.
    !! Require the ExtensionPack !!

[What]
    Utility to interact with Nodegraph Paint Node and Channel Node.
    Function:
        - reset:
             Create a new node that is an exact copy of the current one
             , except it's blank; and delete the original one.
        - get_<node>_info:
            Return a formatted string with info about the Node.

[How]
    - Select an arbitrary number of paintNodes and/or channelNodes
    - Execute the script

[License]
    This work is licensed under PYCO EULA Freelance License Model.

    !! By using this script  you automatically accept and agree to be
    bound by the all the terms described in the EULA. !!

    To view a copy of this license, visit
    https://mrlixm.github.io/PYCO/licenses/eula/

    This license grants the utilisation of the product on personal machines
    (1.c.) used by a single user for Commercial purposes.

    The user may not (a) share (b) distribute any of the content of the
    product, whether it has been modified or not, without an explicit
    agreement from Pyco.

    The user may modify and adapt the content of the product for himself as
    long as the above rules are respected.

"""

import time
import logging

import mari

VERSION = "1.1.0"

logging.basicConfig(level=logging.DEBUG,
                    format='- %(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%H:%M:%S')
logger = logging

logger.info("-- Starting script \n")


def format_colorspace_config(cs_config, indent):
    display_str = "\n"
    display_str += "{} Scalar: {}\n".format(
        ' ' * indent,
        cs_config.scalar())
    display_str += "{} Raw: {}\n".format(
        ' ' * indent,
        cs_config.raw())

    return display_str


class CurrentNodegraphAction(object):
    def __init__(self):
        self.geo = mari.geo.current()
        self.ngc = mari.ExtensionPack.utils.findNodeGraphContext()


class UserSelAction(CurrentNodegraphAction):
    def __init__(self):
        super(UserSelAction, self).__init__()
        self.selections = self.ngc.selectedNodeList()
        if not self.selections:
            raise RuntimeError("Please select at least one node.")

    def check_type(self, node_type):
        """ Raise an error if the node in the selection doesn't correspond
        to the specified type.

        Args:
            node_type(str): typeID of the node that must be checked
        Raises:
            ValueError: if node type is not the one specified
        """
        for node in self.selections:
            if not node.typeID() == node_type:
                raise ValueError("[{}][check_type] "
                                 "The given node <{}> is not a {}"
                                 "".format(self.__class__.__name__,
                                           node.name(),
                                           node_type))
        return

    def check_same_type(self):
        """
        Raises:
            TypeError:
                If all the node in the selection are not of the same
                type.
        """
        base_type = self.selections[0].typeID()
        logger.info("[check_same_type] Base type: {}".format(base_type))
        for user_node in self.selections:
            if user_node.typeID() != base_type:
                raise TypeError("[{}][check_same_type] "
                                "The node <{}> (and maybe other) is not of "
                                "the same type as other node in selection."
                                "".format(self.__class__.__name__,
                                          user_node.name()))
        return

    def get_type_ifsame(self):
        self.check_same_type()
        return self.selections[0].typeID()


class NodeAction(object):
    """
    Perform actions on mari.Node base class
    """
    instance_index = 0

    def __init__(self, node):
        self.node = node
        self.ng = self.node.parentNodeGraph()
        self.instance_index += 1

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, node_obj):
        if not isinstance(node_obj, mari.Node):
            raise TypeError("[{}][node.setter]"
                            "The given object {} is not a Mari node"
                            "".format(self.__class__.__name__,
                                      node_obj))
        self._node = node_obj
        return

    def get_node_info(self):
        """
        Returns:
            str: String formatted with all the node informations
        """
        return self.node.nodeInformation()


class PaintAction(NodeAction):
    """
    Perform actions on a given paint node.
    """

    instance_index = 0

    def __init__(self, paint_node):
        super(PaintAction, self).__init__(paint_node)
        self.paint_node = self.node
        self.instance_index += 1

    @property
    def paint_node(self):
        return self._paint_node

    @paint_node.setter
    def paint_node(self, node):
        if not node.typeID() == "MRI_Misc_Channel_Input":
            raise TypeError("[{}][paint_node.setter]"
                            "The given node {} is not a paint node"
                            "".format(self.__class__.__name__,
                                      node.name()))
        self._paint_node = node
        return

    def get_paint_info(self, indent=4):
        """

        Args:
            indent(int):

        Returns:
            (str): Formatted string with node info.
        """

        display_str = "> PaintNode {}: {}\n".format(self.instance_index,
                                                    self.paint_node.name())
        display_str += "{} Size: {}\n".format(
            ' '*indent,
            self.paint_node.size())
        display_str += "{} Color: {}\n".format(
            ' ' * indent,
            self.paint_node.fillColor().rgba())
        display_str += "{} Bitdepth: {}\n".format(
            ' ' * indent,
            self.paint_node.depth())
        display_str += "{} Colorspace config: {}\n".format(
            ' ' * indent,
            format_colorspace_config(self.paint_node.colorspaceConfig(),
                                     indent*2))

        return display_str

    def reset(self):
        """ Create new paint node that is an exact copy of the current one
        (self), except it's blank, and delete the original one.
        """
        original_name = self.paint_node.name()
        size = int(self.paint_node.size())
        depth = int(self.paint_node.depth())
        color = self.paint_node.fillColor()  # mari.Color
        cs_config = self.paint_node.colorspaceConfig()  # mari.ColorspaceConfig
        original_position = self.paint_node.nodeGraphPosition()
        list_connection = self.paint_node.outputNodes("Output")

        paint_type = mari.Image.FileSpace.FILESPACE_NORMAL
        new_paint = self.ng.createPaintNode(size,
                                            size,
                                            depth,
                                            color,
                                            paint_type,
                                            cs_config)

        new_paint.setName(original_name)
        new_paint.setNodeGraphPosition(original_position)
        # delete the original node from the nodegraph
        self.ng.deleteNode(self.paint_node)
        self.paint_node = new_paint
        # connect the new node
        for target_node, target_port_name in list_connection:
            try:
                target_node.setInputNode(target_port_name, new_paint, "Output")
            except RuntimeError as excp:
                raise RuntimeError("[{}][reset]"
                                   "Can't connect node {} to {} {} port: {}"
                                   "".format(self.__class__.__name__,
                                             original_name,
                                             target_node.name,
                                             target_port_name,
                                             excp))
        logger.info("[{}][reset] "
                    "Node <{}> reset"
                    "".format(self.__class__.__name__,
                              original_name))
        return


class ChannelAction(NodeAction):
    """
    Perform actions on a given paint node.
    """

    instance_index = 0

    def __init__(self, channel_node):
        super(ChannelAction, self).__init__(channel_node)
        self.channel_node = self.node
        self.channel = self.channel_node.channel()
        self.instance_index += 1

    @property
    def channel_node(self):
        return self._channel_node

    @channel_node.setter
    def channel_node(self, node):
        if not node.typeID() == "MRI__System_Shader_Input":
            raise TypeError("[{}][channel_node.setter]"
                            "The given node {} is not a channel node"
                            "".format(self.__class__.__name__,
                                      node.name()))
        self._channel_node = node
        self.channnel = node.channel()
        return

    def get_channel_info(self, indent=4):
        """

        Args:
            indent(int):

        Returns:
            (str): Formatted string with node info.
        """

        display_str = "> ChannelNode {}: {}\n".format(self.instance_index,
                                                    self.channel.name())
        display_str += "{} Size: {}x{}\n".format(
            ' '*indent,
            self.channel.width(),
            self.channel.height())
        display_str += "{} Color: {}\n".format(
            ' ' * indent,
            self.channel.fillColor().rgba())
        display_str += "{} Bitdepth: {}\n".format(
            ' ' * indent,
            self.channel.depth())
        display_str += "{} Colorspace config: {}\n".format(
            ' ' * indent,
            format_colorspace_config(self.channel_node.colorspaceConfig(),
                                     indent * 2))

        return display_str

    def reset(self):
        """ Create new channel node that is an exact copy of the current one
        (self), except it's blank, and delete the original one.
        """
        original_name = self.channel_node.name()
        width, height = self.channel.width(), self.channel.height()
        depth = int(self.channel.depth())
        cs_config = self.channel.colorspaceConfig()  # mari.ColorspaceConfig
        scs_config = self.channel.scalarColorspaceConfig()
        locked = self.channel.isLocked()
        original_position = self.channel_node.nodeGraphPosition()
        list_out_connection = self.channel_node.outputNodes("Output")
        input_node, outport_input_node = mari.ExtensionPack.node.inputNode(
            self.channel_node,
            "Input")

        filespace = mari.Image.FileSpace.FILESPACE_NORMAL
        new_channel = self.ng.createChannelNode(width,
                                                height,
                                                depth,
                                                filespace,
                                                cs_config,)

        new_channel.channel().setLocked(locked)
        new_channel.channel().setScalarColorspaceConfig(scs_config)
        new_channel.setName(original_name)
        new_channel.setNodeGraphPosition(original_position)
        # delete the original node from the nodegraph
        self.ng.deleteNode(self.channel_node)
        self.channel_node = new_channel
        # connect the new node
        # # connect output
        for target_node, target_port_name in list_out_connection:
            try:
                target_node.setInputNode(target_port_name, new_channel, "Output")
            except RuntimeError as excp:
                raise RuntimeError("[{}][reset]"
                                   "Can't connect node {} to {} {} port: {}"
                                   "".format(self.__class__.__name__,
                                             original_name,
                                             target_node.name,
                                             target_port_name,
                                             excp))
        # connect input
        new_channel.setInputNode("Input", input_node, outport_input_node)
        logger.info("[{}][reset] "
                    "Node <{}> reset"
                    "".format(self.__class__.__name__,
                              original_name))
        return


def main():
    start_time = time.clock()

    user_sel = UserSelAction()
    for node in user_sel.selections:

        if node.typeID() == "MRI__System_Shader_Input":
            cha = ChannelAction(channel_node=node)
            cha.reset()

        elif node.typeID() == "MRI_Misc_Channel_Input":
            pa = PaintAction(paint_node=node)
            # print(pa.get_node_info())
            pa.reset()

        else:
            raise TypeError("[main] "
                            "The given node {} is not a channel, neither a "
                            "paint node (not supported.)"
                            "".format(node.name()))

    logger.info("\n Script finished in {}s ".format(
        round(time.clock() - start_time, 3)))


main()
