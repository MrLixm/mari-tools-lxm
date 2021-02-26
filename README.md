**Author:** Liam Collod.

Collections of script I wrote for Foundry's Mari texturing software.

## License

If no LICENSE.md file is clearly specified for a script, OR the _top docstring_ 
doesn't define a License,
 the script is by default shared under `Creative Commons Attribution
 -NonCommercial-ShareAlike 4.0 International` License.

To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/ .



## Utilisation

Everything should be written in the top docstring of each script.
Else a README.md should be supplied.

## What's Inside

- Nodegraph
    - `mari_create_new_channels.py` : 

       Quickly create multiple channels nodes.

    - `mari_group_expose.py`: 

      From a selection of Nodes of same type, expose all of their attribute under the parent GroupNode and link them.

    - `mari_paint_replace.py` : 
    
        Create new Paint Node that is an exact copy of the current one, except it's blank, and delete the original one.
        
        This also work with Channel Nodes.
        
        Also has a method do return a formatted string with Node informations.



Contact: monsieurlixm@gmail.com