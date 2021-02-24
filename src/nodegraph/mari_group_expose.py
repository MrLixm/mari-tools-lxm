"""

Author: Liam Collod
Last Modified: 24/02/2021

[Support]
    Python 2.7+
    Mari SCRIPT
    Tested on Mari 4.7.v1.
    Require the ExtensionPack

[What]
    From a selection of same node type expose all of their attribute under
    the parent GroupNode and linked them.

[License]
    Shared under `Creative Commons Attribution-NonCommercial-ShareAlike 4.0
    International` License.

    To view a copy of this license,
    visit http://creativecommons.org/licenses/by-nc-sa/4.0/.

[Notes]
    Benchmark:
    v01:
        - 5nodes - ~50 attr: 342s
"""
import time
from collections import OrderedDict

import mari

VERSION = "0.0.1"

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
                raise ValueError("[{}][check_type]"
                                 "The given node {} is not a {}"
                                 "".format(self.__class__.__name__,
                                           node.name,
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
                raise TypeError("[{}][check_same_type]"
                                "The node {} (and maybe other) is not of "
                                "the same type as other node in selection."
                                "".format(self.__class__.__name__,
                                          user_node.name))
        return

    def expose_attr_to_parent_group(self, time_pause=True):
        """ Expose all the attributes of the nodes in the selection to the
        parent GroupNode, and link the attribute of each node.

        Args:
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

        knob_dict = OrderedDict()
        for attr_name in first_node.metadataNames():
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


# -----------------------------------------------------------------------------

def main():
    start_time = time.clock()

    user_sel = UserSelAction()
    user_sel.expose_attr_to_parent_group()

    print("\n Script finished in {}s ".format(time.clock() - start_time))


main()

