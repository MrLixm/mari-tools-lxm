"""
Author: Liam Collod
Last Modified: 24/02/2021

[Support]
    Python 2.7+
    Mari SCRIPT
    Tested on Mari 4.7.v1.
    !! Require the ExtensionPack !!

[What]
    Utility to interact with Nodegraph Paint Node.
    Function:
        - reset:
             Create new paint node that is an exact copy of the current one
             , except it's blank; and delete the original one.

[How]
    - Select an arbitrary number of paintNodes
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

import mari

VERSION = "1.0.0"

print("-"*40)


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

        """
        for node in self.selections:
            if not node.typeID() == node_type:
                raise ValueError("[{}][check_type]"
                                 "The given node {} is not a {}"
                                 "".format(self.__class__.__name__,
                                           node.name,
                                           node_type))
        return


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


def main():
    start_time = time.clock()

    user_sel = UserSelAction()
    user_sel.check_type("MRI_Misc_Channel_Input")

    for node in user_sel.selections:
        pa = PaintAction(paint_node=node)
        # print(pa.get_node_info())
        pa.reset()

    print("\n Script finished in {}s ".format(time.clock() - start_time))


main()
