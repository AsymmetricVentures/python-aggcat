from __future__ import absolute_import

import json

from .parser import ObjectifyBase

__all__ = ['JsonObjectify']

class ObjectifyItemBase(object):
    
    def __repr__(self):
        if hasattr(self, '_list'):
            ls = [repr(l) for l in self._list[:2]]
            return '<{} object [{} ...] @ {}>'.format(self._name, ','.join(ls), hex(id(self)))
        else:
            return '<{} object @ {}>'.format(self._name, hex(id(self)))
    
    __len__ = lambda self: len(self._list)
    __iter__ = lambda self: iter(self._list)
    
    def __getattr__(self, name):
        
        if name in self.__dict__:
            return self.__dict__[name]
        
        if name in self._keys:
            tree = self._tree.pop(self._keys[name])
            
            if len(self._tree) == 0:
                type(self)._tree = None
                del type(self)._tree
            
            if isinstance(tree, (list, tuple, dict)):
                obj = self.__parent__._create_from_tree(tree, name = name)
                name = obj._name
            else:
                obj = tree
            
            self.__dict__[name] = obj
            return obj
            
        return getattr(super(type(self), self), name)
    
    def __getitem__(self, idx):
        obj = self._list[idx]
        if not hasattr(obj, '_name'):
            name = '{}item'.format(self.__class__.__name__.lower())
            self._list[idx] = obj = self.__parent__._create_from_tree(obj, name = name)
        return obj
    
    def _eval_tree(self):
        if hasattr(self, '_keys'):
            for v in self._keys.values():
                obj = getattr(self, v)
                if hasattr(obj, '_eval_tree'):
                    obj._eval_tree()
        
        elif hasattr(self, '_list'):
            for obj in self._list:
                if hasattr(obj, '_eval_tree'):
                    obj._eval_tree()
    
    def _to_json(self):
        if hasattr(self, '_list'):
            ret = []
            for obj in self._list:
                if hasattr(obj, '_to_json'):
                    obj = obj._to_json()
                ret.append(obj)
            return ret
        elif hasattr(self, '_keys'):
            ret = {}
            for k in self._keys.values():
                obj = getattr(self, k)
                if hasattr(obj, '_to_json'):
                    obj = obj._to_json()
                ret[k] = obj
            return ret
        else:
            return self

class JsonObjectify(ObjectifyBase):
    application_type = 'application/json'
    error_type = ValueError
    
    def __init__(self, json_str):
        json_data = json.loads(json_str) #: :type json_data: dict
        
        self.obj = self._create_from_tree(json_data)
    
    def _create_from_tree(self, tree, name = None):
        
        if isinstance(tree, dict):
            if len(tree.keys()) == 1:
                # special case for lists
                # Intuit sends down data in the form of `Lists : { ListName : [.. list items ..] }`
                if isinstance(tree.values()[0], (list, tuple)):
                    list_type_name, list_objects = tree.popitem()
                    return self._create_list_object(list_type_name, list_objects)
                
                root_tag, tree = tree.popitem()
                if isinstance(tree, (list, tuple)):
                    return self.clean_tag_name(root_tag, tree)
                else:
                    pass
            else:
                return self._create_object(name, tree)
        elif isinstance(tree, (tuple, list)):
            return self._create_list_object(name, tree)
        else:
            return tree
    
    def _create_object(self, name, tree = None, attributes = None, bases = None):
        name = self.clean_tag_name(name) if name else 'NONAME'
        
        if attributes is None:
            attributes = {}
        
        if bases is None:
            bases = (ObjectifyItemBase,)
        
        attributes.update({
            '__parent__' : self,
            '_name' : name,
            '_keys' : {},
            '_tree' : tree,
        })
        
        if tree is not None:
            attributes['_keys'] = {
                self.clean_tag_name(k) : k for k in tree.keys()
            }
        
        return type(str(name.capitalize()), bases, attributes)()
    
    def _create_list_object(self, name, list_objects = None):
        if list_objects is None:
            list_objects = []
        
        obj = self._create_object(name, attributes = {
            '__parent__' : self,
            '_list' : [],
        }, bases = (ObjectifyItemBase, list))
        
        obj._list = list_objects
        return obj
    
    def get_object(self):
        return self.obj
    
    @classmethod
    def get_credential_fields(cls, institution_details_response):
        fields = []
        
        obj = cls(institution_details_response.content)
        
        for key in obj.keys:
            fields_data = {}
        
        raise NotImplementedError()
        
