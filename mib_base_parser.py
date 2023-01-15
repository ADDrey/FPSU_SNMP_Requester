import string
import os
from io import StringIO

EXEC_DIR = os.path.dirname(os.path.realpath(__file__))
MIB_BASE_PATH = EXEC_DIR + '\\AMICON-FPSU-MIB.my'


class AmiconMIBOIDList():
    def __init__(self, str_mib_file: str, mib_root_name=None, mib_root_id=None):
        # Делаем из файла MIB список строк, для дальнейшего построчного анализа
        str_mib = str_mib_file
        if mib_root_id is None or mib_root_name is None:
            oidTree = Tree()
        else:
            oidTree = Tree(mib_root_name, mib_root_id)
        self.init_mib_tree(str_mib, oidTree)
    

    # Функция формирующая структуру дерева
    def init_mib_tree(self, str_mib: str, oidTree: object):
        s = str_mib
        # Список для значений [Название_параметра, описание, OID].
        oid_list = []
        count = 0
        
        # Формирование дерева значений MIB базы
        while s:
            start_blok = s.find('  a') + 2
            end_blok = s.find(' }\n\n', start_blok) + 2
            mib_obj_blok = s[start_blok: end_blok]
            if '::= {' in mib_obj_blok:
                mib_obj_name, mib_obj_descrip, mib_obj_root, mib_obj_id = self.__get_obj_info_from_mib(mib_obj_blok)
                oid_list.append([mib_obj_name, mib_obj_descrip, 'oid'])
                temp_obj = self.get_tree_obj(oidTree, mib_obj_root)
                if temp_obj is None:
                    print(mib_obj_root, mib_obj_name)
                else: 
                    print(f'Success add {mib_obj_name} object in Node {temp_obj.name}')
                    temp_obj.add_Node(Node(mib_obj_name, mib_obj_descrip, mib_obj_id))
                count += 1
            if start_blok != end_blok:
                s = s[end_blok:]
            else:
                break
        
        # Заполнение списка значений [Название_параметра, описание, OID].
        for obj in oid_list:
            obj[2] = oidTree.obj_id + '.' + (self.get_oid(oidTree, obj[0]))
            #print(obj)
        
        return

        
    # Функция возвращает информацию об объекте MIB базы, получая на вход блок, содержащий инфрмацию об объекте.
    def __get_obj_info_from_mib(self, mib_obj_blok: str):
        s = mib_obj_blok
        mib_obj_name = s[: s.find(' ')].replace(' ', '')
        if s.find('"') == -1:
            mib_obj_descr = ''
        else:
            mib_obj_descr = s[s.find('"') + 1: s.rfind('"')]
        mib_obj_root = s[s.rfind('{ ') + 2: s.find(' ', s.rfind('{ ') + 2)].replace(' ', '')
        mib_obj_id = s[s.rfind(mib_obj_root) + len(mib_obj_root) + 1: s.rfind(' }')].replace(' ', '')
        return mib_obj_name, mib_obj_descr, mib_obj_root, mib_obj_id
    
    
    # Функция собирающая полный OID для объекта в MIB базе по имени объекта
    def get_oid(self, tree: object, obj_name: str) -> str:
        if tree.name == obj_name:
            return ''
        else:
            for child in tree.children:
                if child.name != obj_name and child.children:
                    oid = child.obj_id + '.' + self.get_oid(child, obj_name)
                    if oid == 'Object not found':
                        return 'Object not found'
                    else:
                        return oid
                elif child.name == obj_name and child.descrip:
                    oid = child.obj_id + '.0'
                    if oid == 'Object not found':
                        return 'Object not found'
                    else:
                        return oid
                elif child.name == obj_name and not child.descrip:
                    return child.obj_id
                elif child.name != obj_name and not child.children:
                    continue
        return 'Object not found'

    # Функция возвращающая объект по результату поиска его в дереве
    def get_tree_obj(self, tree: object, obj_name: str) -> object:
        if tree.name == obj_name:
            return tree
        else:
            for child in tree.children:
                if child.name != obj_name and child.children:
                    obj = self.get_tree_obj(child, obj_name)
                    if obj is None:
                        continue
                    elif obj == obj_name:
                        return obj
                elif child.name != obj_name:
                    return None
                elif child.name == obj_name:
                    return child
                elif not child.children:
                    return None


# Класс реализующий Корень (root) древовидной структры данных и добавляющий ссылки на его дочерние объекты
class Tree():
    def __init__(self, name: str='enterprises', descrip: str ='', obj_id: str ='.1.3.6.1.4.1'):
        self.name = name
        self.descrip = descrip
        self.obj_id = obj_id
        self.children = []
        
        
    def add_Node(self, obj: object):
        self.children.append(obj)
        
        
# Класс реализующий Узел (Node) древовидной структры данных и добавляющий ссылки на его дочерние объекты        
class Node():
    def __init__(self, name: str, descrip: str, obj_id: str):
        self.obj_id = obj_id
        self.name = name
        self.descrip = descrip
        self.children = []
        
        
    def add_Node(self, obj: object):
        self.children.append(obj)


# Точка входа в программу
if __name__ == "__main__":
    mib_file_path = open(MIB_BASE_PATH).read()
    OID_Base = AmiconMIBOIDList(mib_file_path)
