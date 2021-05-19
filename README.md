# simple-data-editor
A simple implementation of data editor by Python. Using tkinter package for visualization. UIs are ugly. Just for fun. Made in 2020/7.

It stores and reads info using json file. For opening a json file, it either supports a path or through the file explorer.

It stores infomation in the form index: content. You can imagine it as opening several txt editor at the same window. It also supports functionality including saving, searching index, creating new index, deleting existing index, undo and redo.

I created this program to gain some experience of python visualizing, so the codes are not perfect, neither are the functions. 
One possible direction I can improve these codes (if I have time) is to seperate the visualization codes from the codes that manage the little database. For now, they are combined together (as you can see, there are only 2 py files now). 
Other improvements may include adding colors for texts, adding hyperlinks and even inserting pictures (perhaps a simplified Office Word that supports editing multiple files under the same window?). 
