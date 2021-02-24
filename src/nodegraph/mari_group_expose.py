"""

Author: Liam Collod
Last Modified: 24/02/2021

[Support]
    Python 2.7+
    Mari SCRIPT
    Tested on Mari 4.7.v1.
    !! Require the ExtensionPack !!

[What]
    From a selection of same node type expose all of their attribute under
    the parent GroupNode and linked them.

[How]
    - Select a bunch of node of the same type inside a Group Node
    - Execute this script
    - (optionnal) Add attributes names that you would like to not expose in
        <attr_ignore_list> list in the main() function.

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

[Notes]
    Benchmark:
    v0.0.1:
        - 5nodes (heavy) - ~60 attr: 342s (time_sleep=True)
    v0.0.2:
        - 6nodes - 3attr: 0.0534s (time_sleep=False)

"""
import time
from collections import OrderedDict

import mari

VERSION = "1.0.0"

print("-"*40)


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
        print("[check_same_type] Base type: {}".format(base_type))
        for user_node in self.selections:
            if user_node.typeID() != base_type:
                raise TypeError("[{}][check_same_type] "
                                "The node <{}> (and maybe other) is not of "
                                "the same type as other node in selection."
                                "".format(self.__class__.__name__,
                                          user_node.name()))
        return

    def expose_attr_to_parent_group(self, time_pause=False,
                                    attr_ignore_list=None):
        """ Expose all the attributes of the nodes in the selection to the
        parent GroupNode, and link the attribute of each node.

        Args:
            attr_ignore_list(list of str or tuple of str):
                List of attributes name that need to be ignored/skipped.

            time_pause(bool): If True the script will paude for few second
                between each operation.
                It was noticed that this might help Mari on processing a lot
                of attributes.
        """
        # checkup
        self.check_same_type()

        group_node = self.ngc.parentGroupNode()
        if not group_node:
            raise TypeError(
                "[{}][expose_attr_to_parent_group]"
                " Current nodegraph is not part of a GroupNode"
                "".format(self.__class__.__name__))

        first_node = self.selections[0]

        # create a dictionnary with all the attributes that need to be exposed
        knob_dict = OrderedDict()
        for attr_name in first_node.metadataNames():
            if attr_ignore_list and attr_name in attr_ignore_list:
                continue  # skip this attribute
            knob_dict[attr_name] = []  # init with an empty object

        # Create the knobs on the group node for each node in the selection
        print("[{}][expose_attr_to_parent_group]"
              " attributes number: {}".format(self.__class__.__name__,
                                              len(knob_dict)))

        for index, source_node in enumerate(self.selections):
            for _attr_name in knob_dict.keys():
                # give a different name for each knob so add the index.
                new_knob_name = "{}_{}".format(_attr_name, index)
                if not knob_dict.get(_attr_name):
                    # if the value is empty create the value (list)
                    knob_dict[_attr_name] = [new_knob_name]
                else:
                    # there is already a list value so modify it
                    knob_dict[_attr_name].append(new_knob_name)

                group_node.createKnob(
                    new_knob_name,  # knob name
                    source_node,
                    _attr_name,  # TargetAttributeName of the source_node
                    source_node.metadataDisplayName(_attr_name)  # pretty name
                )
                time.sleep(0.5) if time_pause else None
                # print("knob created: {}".format(new_knob_name))
                continue
            continue

        time.sleep(20) if time_pause else None

        # Link the knobs on the group node
        for _attr_name, knob_list in knob_dict.items():
            try:
                group_node.linkKnobs(
                    _attr_name,
                    knob_list,
                    first_node.metadataDisplayName(_attr_name)  # pretty name
                )
                time.sleep(1) if time_pause else None
            except Exception as excp:
                print("[ ERROR ][expose_node_attr_to_group] "
                      " linkKnobs error: {}".format(excp))
            continue

    def get_infos(self, first_item_only=False):
        """

        Args:
            first_item_only(bool):
                return only the node information for the
                first item in the selection.

        Returns:
            str: node information
        """
        if first_item_only:
            return self.selections[0].nodeInformation()

        display_str = ""
        for node in self.selections:
            display_str += node.nodeInformation()

        return display_str


# -----------------------------------------------------------------------------

def main():
    start_time = time.clock()

    user_sel = UserSelAction()
    # print(user_sel.get_infos())
    attr_ignore_list = [""]
    user_sel.expose_attr_to_parent_group(time_pause=False,
                                         attr_ignore_list=attr_ignore_list)

    print("\n Script finished in {}s ".format(time.clock() - start_time))


main()

