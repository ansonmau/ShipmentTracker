class Select:
    def __init__(self, wds):
        pass
    
    def by_text(self, select_elm, text):
        select_elm.select_by_visible_text(text) 

    def by_value(self, select_elm, attr):
        select_elm.select_by_value(attr)

    def by_index(self, select_elm, index):
        select_elm.select_by_index(index)
        
