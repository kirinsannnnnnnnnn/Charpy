import os
import os.path

print('my_module/reader.py is loaded')


class Directory():
    def __init__(self, name):
        self.name = name
        self.root = False
        self.parent = None

    @classmethod
    def isfile(cls): return True if cls.__name__ == "File" else False

    @classmethod
    def isfolder(cls): return True if cls.__name__ == "Folder" else False

    def havechild(self): return True if not self.child == None else False

    def haveparent(self): return True if not self.parent == None else False

    def get_depth(self, dire):
        i = 0
        while dire.haveparent():
            i += 1
            dire = dire.parent
        return i


class File(Directory):
    def __init__(self, name, dire):
        Directory.__init__(self, name)
        self.parent = dire
        self.child = None
        self.depth = self.get_depth(self)

    def get_path(self): return self.parent.get_path() + "/" + self.name

    def add_child(self): return False

    def get_parent(self): return self.parent


class Folder(Directory):
    def __init__(self, name, parent=False):
        Directory.__init__(self, name)
        self.child = []
        self.childname = []
        self.file = []
        if parent:
            self.parent = parent
        self.depth = self.get_depth(self)

    def add_parent(self, parent):
        if parent.name in self.parent.name:
            self.parent = parent
            return True

    def add_child(self, child):
        if child.name not in self.childname:
            self.child.append(child)
            self.childname.append(child.name)
            return True
        else:
            return False

    def set_root(self): self.root = True

    def get_parent(self): return self.parent

    def get_path(self):
        cur_path = self.name
        if not self.root:
            cur_path = self.parent.get_path() + "/" + cur_path
        return cur_path

    def get_children_file_list(self):
        cur_list = []
        if self.havechild():
            for ele in self.child:
                if ele.isfile():
                    cur_list.append(ele)
                else:
                    cur_list.extend(ele.get_children_file_list())
        return cur_list

    def make_folder(self, name):
        if name not in self.childname:
            new_path = self.get_path() + "/" + name
            if not os.path.exists(new_path):
                os.makedirs(new_path)
            cur_fol = Folder(name, self)
            self.add_child(cur_fol)
            return cur_fol
        return False

    def child_exist(self, name): return True if name in self.childname else False


class Dir_tree():
    def __init__(self):
        self.root = None
        self.file_list = []
        self.folder_list = []
        self.depth = []
        self.depth_list = []

    def set_root_dir(self, root_name):
        self.root = Folder(root_name)
        self.root.set_root()
        self.file_list, cur_list, self.folder_list = self.get_tree(self.root)
        self.folder_list = [self.root] + self.folder_list
        self.file_depth_list = [ele.get_depth(ele) for ele in self.file_list]
        if len(self.file_depth_list) > 0:
            self.depth_max, self.depth_min = max(self.file_depth_list), min(self.file_depth_list)
            self.depth = [self.depth_min, self.depth_max]

    def add_dir_parent(self, dire, parent):
        if dire.add_parent(parent):
            self.folder_list.append(parent)

    def add_dir_child(self, dire, child):
        if dire.add_child(child):
            self.folder_list.append(child)

    def search_dir(self, dir_name):
        for dire in self.folder_list:
            if dire.name == dir_name:
                return dire
        return False

    def get_tree(self, dire):
        cur_file_list = []
        cur_folder_list = []
        fin_fol_lis = []
        for ele in os.listdir(dire.get_path()):
            if os.path.isdir(dire.get_path() + "/" + ele):
                ele = Folder(ele, dire)
                self.add_dir_child(dire, ele)
                cur_folder_list.append(ele)
            else:
                ele = File(ele, dire)
                self.add_dir_child(dire, ele)
                cur_file_list.append(ele)
        while cur_folder_list:
            if cur_folder_list[0].isfile():
                print(__name__, 1, cur_folder_list[0])
            s_fil, s_fol, s_fin_fol = self.get_tree(cur_folder_list[0])
            fin_fol_lis.append(cur_folder_list.pop(0))
            cur_file_list.extend(s_fil)
            cur_folder_list.extend(s_fol)
            fin_fol_lis.extend(s_fin_fol)

        return cur_file_list, cur_folder_list, fin_fol_lis

    def copy_tree(self, depth, cfol, dfol, tree):
        if depth == 0:
            return tree
        for ele in cfol.child:
            if ele.isfolder():
                cur_child = dfol.make_folder(ele.name)
                if not cur_child:
                    for ch_ele in dfol.child:
                        if ele.name == ch_ele.name:
                            cur_child = ch_ele

                self.copy_tree(depth - 1, ele, cur_child, tree)

        tree.file_list, cur_list, tree.folder_list = tree.get_tree(tree.root)
        tree.folder_list = [tree.root] + tree.folder_list
        tree.file_depth_list = [ele.get_depth(ele) for ele in tree.file_list]
        if len(self.file_depth_list) > 0:
            tree.depth_max, tree.depth_min = max(tree.file_depth_list), min(tree.file_depth_list)
            tree.depth = [tree.depth_min, tree.depth_max]

        return tree

    def tespri(self):
        print("files are ", len(self.file_list))
        print("folders are ", len(self.folder_list))


class Reader(Dir_tree):
    def __init__(self, name=None):
        Dir_tree.__init__(self)
        if name:
            self.set_root_dir(name)

    # def set_root(self, name):
    #     self.root_name = name
    #     self.set_root_dir(self.root_name)

    def get_root_folder(self): return self.root

    def get_depth_file_list(self, depth): return [ele for ele in self.file_list if ele.depth == depth]

    def get_children_file_list(self, dire):
        return dire.get_children_file_list()

    def get_children_ext_files_dict(self, dire_list, ext):
        dic = {}
        for key in dire_list:
            dic[key] = [ele for ele in key.get_children_file_list() if ele.name.find(ext) > 0]
            # break #hereeeeeeeeeeeeeeeeeeeeeeeeee
        return dic

    def get_children_ext_files_list(self, dire, ext):
        return [ele for ele in dire.get_children_file_list() if ele.name.find(ext) > 0]

    def copy_tree_to_here(self, creader, depth):
        self.copy_tree(depth, creader.dir_tree.root, self.root, self)  # def copy_tree(self, depth, cfol, dfol, tree):

    def make_dir(self, parent_dir, adding_dir_name):
        return parent_dir.make_folder(adding_dir_name)

    def test_exe(self):
        print(111, __name__, self.file_depth_list)
        print(222, __name__, self.depth)
        print(333, __name__, self.get_depth_file_list(self.root))


if __name__ == "__main__":
    rd = Reader("data")
    rd.test_exe()
    rd.tespri()
