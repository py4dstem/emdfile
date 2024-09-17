from emdfile import save, read
from emdfile import Node,Root,Metadata,Array,PointList,PointListArray
from emdfile.utils import _is_EMD_file,_get_EMD_rootgroups
import numpy as np
import h5py
import pytest
import tempfile
from pathlib import Path


class TestTree:

    @pytest.fixture
    def testpath(self):
        """Create an empty temporary file and return as a Path."""
        tf = tempfile.NamedTemporaryFile(mode='wb')
        tf.close()  # need to close the file to use it later
        return Path(tf.name)

    @pytest.fixture
    def tree(self):
        """
        Builds the following tree:

        Root                  'root'
          |-Metadata          'metadata_root'
          |-Metadata          'metadata_root2'
          |-PointList         'pointlist3'
          | |-PointList       'pointlist4'
          |   |-Metadata      'metadata3'
          |-Array             'array
            |-Metadata        'metadata'
            |-Metadata        'metadata2'
            |-PointListArray  'pointlistarray'
              |-PointList     'pointlist'
              |-PointList     'pointlist2'
        """
        # make some objects
        # root
        root = Root(name='root')
        # array
        ar = Array(name='array',data=np.array([[1,2],[3,4]]))
        # pointlist
        pl = PointList(
            data = np.zeros(
                5,
                dtype = [
                    ('x',float),
                    ('y',float)
                ]
            ),
            name = 'pointlist',
        )
        pl2 = PointList(
            data = np.ones(
                4,
                dtype = [
                    ('qx',float),
                    ('qy',float)
                ]
            ),
            name = 'pointlist2'
        )
        pl3 = PointList(
            data = np.ones(
                8,
                dtype = [
                    ('r',float),
                    ('theta',float)
                ]
            ),
            name = 'pointlist3'
        )
        pl4 = PointList(
            data = np.ones(
                7,
                dtype = [
                    ('z',float),
                    ('c',float)
                ]
            ),
            name = 'pointlist4'
        )
        # pointlistarray
        pla = PointListArray(
            shape = (3,4),
            dtype = [
                ('a',float),
                ('b',float)
            ]
        )
        # metadata
        md = Metadata()
        md._params.update({
            'duck':'steve'
        })
        md2 = Metadata(name='metadata2')
        md2._params.update({
            'duck':'steven'
        })
        md3 = Metadata(name='metadata3')
        md3._params.update({
            'duck':'stevo'
        })
        md_root = Metadata(name='metadata_root')
        md_root._params.update({
            'cow':'ben'
        })
        md_root2 = Metadata(name='metadata_root2')
        md_root2._params.update({
            'cow':'benjamin'
        })
        # construct tree
        root.metadata = md_root
        root.metadata = md_root2
        root.tree(pl3)
        pl3.tree(pl4)
        pl4.metadata = md3
        root.tree(ar)
        ar.metadata = md
        ar.metadata = md2
        ar.tree(pla)
        pla.tree(pl)
        pla.tree(pl2)
        # return
        return root

    @pytest.fixture
    def tree2(self):
        """
        Make another tree:

        Root                  'root2'
          |-Array             'array2'
            |-PointList       'pointlist5'
        """
        root2 = Root(name='root2')
        ar2 = Array(
            data = np.array([[10,20,30],[40,50,60]]),
            name = 'array2')
        pl5 = PointList(
            data = np.ones(
                6,
                dtype = [
                    ('l',float),
                    ('m',float)
                ]
            ),
            name = 'pointlist5'
        )
        # construct tree
        root2.tree(ar2)
        ar2.tree(pl5)
        return root2

    @pytest.fixture
    def unrooted_array(self):
        """make an unrooted array"""
        ar_unrooted = Array(
            data = np.array([[5,6],[7,8]]),
            name = 'unrooted_array')
        # set array dimensions
        ar_unrooted.set_dim(
            0,
            dim = 0.25,
            units = 'ponies',
            name = 'pony_axis')
        ar_unrooted.set_dim( 1, dim = [0,1.5] )
        ar_unrooted.set_dim_units(1,'cows')
        return ar_unrooted

    @staticmethod
    def pointlist_equal(pl1,pl2):
        """
        Return true iff pl1 and pl2 are equal
        """
        # allow for pl1 and pl2 to have the same fields in different order
        k1,k2 = pl1.fields,pl2.fields
        assert(all([k in k1 for k in k2]))
        assert(all([k in k2 for k in k1]))
        for k in k1:
            try:
                assert(np.array_equal(pl1.data[k],pl2.data[k]))
            except AssertionError:
                return False
        return True

    # Tests

    # Node retrieval and paths

    def test_tree_nodes(self,testpath,tree):
        """Retrieve nodes and metadata and confirm correct types"""
        assert(isinstance(tree,Node))
        assert(isinstance(tree,Root))
        assert(isinstance(tree.metadata['metadata_root'],Metadata))
        assert(not(isinstance(tree.metadata['metadata_root'],Node)))
        assert(isinstance(tree.metadata['metadata_root2'],Metadata))
        assert(not(isinstance(tree.metadata['metadata_root2'],Node)))
        assert(isinstance(tree.tree('pointlist3'),Node))
        assert(isinstance(tree.tree('pointlist3'),PointList))
        assert(isinstance(tree.tree('pointlist3/pointlist4'),Node))
        assert(isinstance(tree.tree('pointlist3/pointlist4'),PointList))
        assert(isinstance(tree.tree('pointlist3/pointlist4').metadata['metadata3'],Metadata))
        assert(not(isinstance(tree.tree('pointlist3/pointlist4').metadata['metadata3'],Node)))
        assert(isinstance(tree.tree('array'),Node))
        assert(isinstance(tree.tree('array'),Array))
        assert(isinstance(tree.tree('array/pointlistarray'),Node))
        assert(isinstance(tree.tree('array/pointlistarray'),PointListArray))
        assert(isinstance(tree.tree('array/pointlistarray/pointlist'),Node))
        assert(isinstance(tree.tree('array/pointlistarray/pointlist'),PointList))
        assert(isinstance(tree.tree('array/pointlistarray/pointlist2'),Node))
        assert(isinstance(tree.tree('array/pointlistarray/pointlist2'),PointList))
        assert(isinstance(tree.tree('array').metadata['metadata'],Metadata))
        assert(not(isinstance(tree.tree('array').metadata['metadata'],Node)))
        assert(isinstance(tree.tree('array').metadata['metadata2'],Metadata))
        assert(not(isinstance(tree.tree('array').metadata['metadata2'],Node)))
        # confirm root path notation i.e. leading '/'
        ar = tree.tree('array')
        assert(ar.tree('/array') == ar)
        assert(ar.tree('pointlistarray').tree('/array') == ar)
        # confirm correct ._treepath attrs
        assert(ar._treepath == '/array')
        # confirm that all nodes point to the same root node
        assert(tree.root == ar.root == tree.tree('pointlist3').root)
        # save/read
        save(testpath,tree)
        t2 = read(testpath)
        # re-check
        assert(isinstance(t2,Node))
        assert(isinstance(t2,Root))
        assert(isinstance(t2.metadata['metadata_root'],Metadata))
        assert(not(isinstance(t2.metadata['metadata_root'],Node)))
        assert(isinstance(t2.metadata['metadata_root2'],Metadata))
        assert(not(isinstance(t2.metadata['metadata_root2'],Node)))
        assert(isinstance(t2.tree('pointlist3'),Node))
        assert(isinstance(t2.tree('pointlist3'),PointList))
        assert(isinstance(t2.tree('pointlist3/pointlist4'),Node))
        assert(isinstance(t2.tree('pointlist3/pointlist4'),PointList))
        assert(isinstance(t2.tree('pointlist3/pointlist4').metadata['metadata3'],Metadata))
        assert(not(isinstance(t2.tree('pointlist3/pointlist4').metadata['metadata3'],Node)))
        assert(isinstance(t2.tree('array'),Node))
        assert(isinstance(t2.tree('array'),Array))
        assert(isinstance(t2.tree('array/pointlistarray'),Node))
        assert(isinstance(t2.tree('array/pointlistarray'),PointListArray))
        assert(isinstance(t2.tree('array/pointlistarray/pointlist'),Node))
        assert(isinstance(t2.tree('array/pointlistarray/pointlist'),PointList))
        assert(isinstance(t2.tree('array/pointlistarray/pointlist2'),Node))
        assert(isinstance(t2.tree('array/pointlistarray/pointlist2'),PointList))
        assert(isinstance(t2.tree('array').metadata['metadata'],Metadata))
        assert(not(isinstance(t2.tree('array').metadata['metadata'],Node)))
        assert(isinstance(t2.tree('array').metadata['metadata2'],Metadata))
        assert(not(isinstance(t2.tree('array').metadata['metadata2'],Node)))
        # confirm root path notation i.e. leading '/'
        ar = t2.tree('array')
        assert(ar.tree('/array') == ar)
        assert(ar.tree('pointlistarray').tree('/array') == ar)
        # confirm correct ._treepath attrs
        assert(ar._treepath == '/array')
        # confirm that all nodes point to the same root node
        assert(t2.root == ar.root == t2.tree('pointlist3').root)


    # Cut

    def test_branchcut(self,tree):
        """
        Confirms correct branch cutting behavior
        for default metadata behavior (transfer root metadata)
        """
        # cutting off a branch
        pl4 = tree.tree('pointlist3/pointlist4')
        new_root = pl4.tree(cut=True)
        assert(pl4.root == new_root)
        assert(new_root.tree('pointlist4') == pl4)
        assert(new_root.metadata == tree.metadata)

    def test_branchcut_no_metadata(self,tree):
        """
        Confirms correct branch cutting behavior
        without transferring old root metadata
        """
        # cutting off a branch
        pl4 = tree.tree('pointlist3/pointlist4')
        new_root = pl4.tree(cut=False)
        assert(len(new_root.metadata)==0)

    def test_branchcut_copy_metadata(self,tree):
        """
        Confirms correct branch cutting behavior
        when copying root metadata
        """
        # cutting off a branch
        pl4 = tree.tree('pointlist3/pointlist4')
        new_root = pl4.tree(cut='copy')
        assert(len(new_root.metadata)==2)
        assert(new_root.metadata != tree.metadata)

    # Graft

    def test_graft(self,tree):
        """
        Confirms correct grafting behavior
        """
        pl4 = tree.tree('pointlist3/pointlist4')
        pla = tree.tree('array/pointlistarray')
        # make a new tree to graft onto
        new_root = pl4.tree(cut=True)
        # graft
        pla.tree( graft=new_root.tree('pointlist4') )
        # check
        data = tree.tree('array/pointlistarray/pointlist4')
        assert(isinstance(data,PointList))
        assert(data == pl4)

    def test_graft2(self,tree):
        """
        Confirms correct grafting behavior with alternative syntax
        """
        pl4 = tree.tree('pointlist3/pointlist4')
        pla = tree.tree('array/pointlistarray')
        # make a new tree to graft onto
        new_root = pl4.tree(cut=True)
        # graft
        pla.graft( new_root.tree('pointlist4') )
        # check
        data = tree.tree('array/pointlistarray/pointlist4')
        assert(isinstance(data,PointList))
        assert(data == pl4)

    def test_graft3(self,tree):
        """
        Confirms correct grafting behavior with alternative syntax
        """
        pl4 = tree.tree('pointlist3/pointlist4')
        pla = tree.tree('array/pointlistarray')
        # make a new tree to graft onto
        new_root = pl4.tree(cut=True)
        # graft
        pla.tree( graft=(new_root.tree('pointlist4'),True) )
        # check
        data = tree.tree('array/pointlistarray/pointlist4')
        assert(isinstance(data,PointList))
        assert(data == pl4)

    # Write

    def test_write_single_node(self,tree,testpath):
        ar = tree.tree('array')
        save( testpath,ar,tree=False )
        ar2 = read( testpath )
        assert(np.array_equal(ar.data,ar2.data))

    def test_write_unrooted_node(self,testpath,unrooted_array):
        save( testpath,unrooted_array )
        ar2 = read( testpath )
        assert(np.array_equal(unrooted_array.data, ar2.data))

    def test_write_whole_tree(self,testpath,tree):
        save(testpath,tree,tree=True)
        tree2 = read(testpath)
        assert(np.array_equal(tree.tree('array').data,tree2.tree('array').data))

    def test_write_h5_subtree(self,testpath,tree):
        """Write a subtree to file"""
        pl3 = tree.tree('pointlist3')
        save(testpath,pl3,tree=True)
        tree2 = read(testpath)
        assert(self.pointlist_equal(
            pl3.tree('pointlist4'),tree2.tree('/pointlist3/pointlist4')))

    def test_write_h5_subtree_noroot(self,testpath,tree):
        """Write a subtree to file without it's root dataset"""
        pl3 = tree.tree('pointlist3')
        save(testpath,pl3,tree=None)
        tree2 = read(testpath)
        assert(self.pointlist_equal(
            pl3.tree('pointlist4'),tree2.tree('/pointlist4')))

    # Append

    def test_append_to_h5(self,testpath,tree,tree2):
        """
        Append to an existing h5 file
        """
        ar = tree.tree('array')
        ar2 = tree2.tree('array2')
        save(testpath,ar,tree=False)
        save(testpath,ar2,tree=True,mode='a')
        tree3 = read(testpath,emdpath='root')
        tree4 = read(testpath,emdpath='root2')
        assert(np.array_equal(ar.data,tree3.data))
        assert(np.array_equal(ar2.data,tree4.data))
        pass

    def test_append_over_h5(self,testpath,tree,tree2):
        """
        Append to an existing h5 file, overwriting a redundantly named object
        """
        ar = tree.tree('array')
        ar2 = tree2.tree('array2')
        ar2.root.name = 'root'
        save(testpath,ar,tree=False)
        save(testpath,ar2,tree=True,mode='ao')
        tree3 = read(testpath)
        assert(not(np.array_equal(ar.data,tree3.tree('array2').data)))
        assert(np.array_equal(ar2.data,tree3.tree('array2').data))
        pass

    # More

    def test_is_EMD_file(self,testpath,tree):
        save(testpath,tree)
        assert(_is_EMD_file(testpath))

    def test_hdf5_paths(self,testpath,tree):
        """
        Confirms that the _treepath is always the same as
        the group path without its root
        """
        save(testpath,tree)
        # Open the file
        with h5py.File(testpath,'r') as f:
            # loop over nodes
            for node in (
                tree.root,
                tree.tree('array'),
                tree.tree('pointlist3'),
                tree.tree('pointlist3/pointlist4'),
                tree.tree('array/pointlistarray'),
                tree.tree('array/pointlistarray/pointlist'),
                tree.tree('array/pointlistarray/pointlist2'),
            ):
                assert( f[f'/{tree.root.name}/' + node._treepath] )

    # IO

    def test_emdpath(self,testpath,tree):
        """Test the `emdpath` argument"""
        save(testpath,tree)
        # no emdpath
        t = read(testpath)
        assert(isinstance(t,Root))
        # test emdpath
        t = read(testpath,emdpath='/root/array')
        assert(isinstance(t,Array))
        t = read(testpath,emdpath='root/array')
        assert(isinstance(t,Array))
        t = read(testpath,emdpath='/root/array/pointlistarray')
        assert(isinstance(t,PointListArray))

    def test_unrooted_node(self,testpath,unrooted_array):
        """Test unrooted node behavior"""
        save(testpath,unrooted_array)
        t = read(testpath)
        assert(not(isinstance(t,Root)))
        assert(isinstance(t,Array))
        assert(isinstance(t.root,Root))
        assert(t.root.name=='unrooted_array_root')



#    def test_whole_tree_io(self):
#        """ Should contain the full data tree:
#
#            Root                  'root'
#              |-Metadata          'metadata_root'
#              |-Metadata          'metadata_root'
#              |-PointList         'pointlist3'
#              | |-PointList       'pointlist4'
#              |   |-Metadata      'metadata3'
#              |-Array             'array
#                |-Metadata        'metadata'
#                |-Metadata        'metadata2'
#                |-PointListArray  'pointlistarray'
#                  |-PointList     'pointlist'
#                  |-PointList     'pointlist2'
#        """
#        # Load data
#        loaded_data = read(
#            whole_tree_path
#        )
#
#        # Does the tree look as it should?
#        assert(isinstance(loaded_data,Root))
#        assert(loaded_data.name == 'root')
#
#        lmd_root = loaded_data.metadata['metadata_root']
#        lmd_root2 = loaded_data.metadata['metadata_root2']
#        lpl3 = loaded_data.tree('/pointlist3')
#        lpl4 = loaded_data.tree('pointlist3/pointlist4')
#        lmd3 = lpl4.metadata['metadata3']
#        lar = loaded_data.tree('array')
#        lmd = lar.metadata['metadata']
#        lmd2 = lar.metadata['metadata2']
#        lpla = loaded_data.tree('array/pointlistarray')
#        lpl = loaded_data.tree('array/pointlistarray/pointlist')
#        lpl2 = loaded_data.tree('array/pointlistarray/pointlist2')
#
#        # Check types
#        assert(isinstance(lmd_root,Metadata))
#        assert(isinstance(lmd_root2,Metadata))
#        assert(isinstance(lpl3,PointList))
#        assert(isinstance(lpl4,PointList))
#        assert(isinstance(lmd3,Metadata))
#        assert(isinstance(lar,Array))
#        assert(isinstance(lmd,Metadata))
#        assert(isinstance(lmd2,Metadata))
#        assert(isinstance(lpla,PointListArray))
#        assert(isinstance(lpl,PointList))
#        assert(isinstance(lpl2,PointList))
#
#        # New objects are distinct from old objects
#        assert(lmd_root is not self.md_root)
#        assert(lmd_root2 is not self.md_root2)
#        assert(lpl3 is not self.pl3)
#        assert(lpl4 is not self.pl4)
#        assert(lmd3 is not self.md3)
#        assert(lar is not self.ar)
#        assert(lmd is not self.md)
#        assert(lmd2 is not self.md2)
#        assert(lpla is not self.pla)
#        assert(lpl is not self.pl)
#        assert(lpl2 is not self.pl2)
#
#        # New objects carry identical data to old objects
#        assert(lmd_root._params == self.md_root._params)
#        assert(lmd_root2._params == self.md_root2._params)
#        assert(self.pointlist_equal(lpl3, self.pl3))
#        assert(self.pointlist_equal(lpl4, self.pl4))
#        assert(lmd3._params == self.md3._params)
#        assert(array_equal(lar.data, self.ar.data))
#        assert(lmd._params == self.md._params)
#        assert(lmd2._params == self.md2._params)
#        assert(self.pointlist_equal(lpl, self.pl))
#        assert(self.pointlist_equal(lpl2, self.pl2))
#        for x in range(lpla.shape[0]):
#            for y in range(lpla.shape[1]):
#                assert(self.pointlist_equal(lpla[x,y], self.pla[x,y]))
#
#        pass
#
#
#    def test_whole_tree_io_treeIsFalse(self):
#        """ Should contain only:
#
#            Root                  'root'
#              |-PointListArray    'pointlistarray'
#        """
#        # Load data
#        loaded_data = read(
#            whole_tree_path,
#            emdpath = '/root/array/pointlistarray',
#            tree = False
#        )
#
#        # Does the tree look as it should?
#        assert(isinstance(loaded_data,PointListArray))
#        assert(loaded_data.name == 'pointlistarray')
#
#        lmd_root = loaded_data.root.metadata['metadata_root']
#        lmd_root2 = loaded_data.root.metadata['metadata_root2']
#
#        # Check types
#        assert(isinstance(lmd_root,Metadata))
#        assert(isinstance(lmd_root2,Metadata))
#
#        # New objects are distinct from old objects
#        assert(lmd_root is not self.md_root)
#        assert(lmd_root2 is not self.md_root2)
#        assert(loaded_data is not self.pla)
#
#        # New objects carry identical data to old objects
#        assert(lmd_root._params == self.md_root._params)
#        assert(lmd_root2._params == self.md_root2._params)
#        for x in range(loaded_data.shape[0]):
#            for y in range(loaded_data.shape[1]):
#                assert(self.pointlist_equal(loaded_data[x,y], self.pla[x,y]))
#
#        pass
#
#
#    def test_subtree_io(self):
#        """ Tree should be root/pointlist3/pointlist4, plus
#        metadata at root and pl4
#        """
#        # Load data
#        loaded_data = read(
#            subtree_path
#        )
#
#        # Does the tree look as it should?
#        assert(isinstance(loaded_data,PointList))
#        assert(loaded_data.name == 'pointlist3')
#
#        lmd_root = loaded_data.root.metadata['metadata_root']
#        lmd_root2 = loaded_data.root.metadata['metadata_root2']
#        lpl3 = loaded_data
#        lpl4 = loaded_data.tree('pointlist4')
#        lmd3 = lpl4.metadata['metadata3']
#
#        # Check types
#        assert(isinstance(lmd_root,Metadata))
#        assert(isinstance(lmd_root2,Metadata))
#        assert(isinstance(lpl3,PointList))
#        assert(isinstance(lpl4,PointList))
#        assert(isinstance(lmd3,Metadata))
#
#        # New objects are distinct from old objects
#        assert(lmd_root is not self.md_root)
#        assert(lmd_root2 is not self.md_root2)
#        assert(lpl3 is not self.pl3)
#        assert(lpl4 is not self.pl4)
#        assert(lmd3 is not self.md3)
#
#        # New objects carry identical data to old objects
#        assert(lmd_root._params == self.md_root._params)
#        assert(lmd_root2._params == self.md_root2._params)
#        assert(self.pointlist_equal(lpl3, self.pl3))
#        assert(self.pointlist_equal(lpl4, self.pl4))
#        assert(lmd3._params == self.md3._params)
#
#        pass
#
#
#
#    def test_subtree_noroot_io(self):
#        """ Tree should be root/pointlist4, plus
#        metadata at root and pl4
#        """
#        # Load data
#        loaded_data = read(
#            subtree_noroot_path
#        )
#
#        # Does the tree look as it should?
#        assert(isinstance(loaded_data,PointList))
#        assert(loaded_data.name == 'pointlist4')
#
#        lmd_root = loaded_data.root.metadata['metadata_root']
#        lmd_root2 = loaded_data.root.metadata['metadata_root2']
#        lpl4 = loaded_data
#        lmd3 = lpl4.metadata['metadata3']
#
#        # Check types
#        assert(isinstance(lmd_root,Metadata))
#        assert(isinstance(lmd_root2,Metadata))
#        assert(isinstance(lmd3,Metadata))
#
#        # New objects are distinct from old objects
#        assert(lmd_root is not self.md_root)
#        assert(lmd_root2 is not self.md_root2)
#        assert(lpl4 is not self.pl4)
#        assert(lmd3 is not self.md3)
#
#        # New objects carry identical data to old objects
#        assert(lmd_root._params == self.md_root._params)
#        assert(lmd_root2._params == self.md_root2._params)
#        assert(self.pointlist_equal(lpl4, self.pl4))
#        assert(lmd3._params == self.md3._params)
#
#        pass
#
#
#    def test_append_to_io(self):
#        """ Tree should be
#                root
#                    |--array
#                        |--pointlist5
#        """
#        # Load data
#        loaded_data = read(
#            subtree_append_to_path
#        )
#
#        # Does the tree look as it should?
#        assert(isinstance(loaded_data,Array))
#        assert(loaded_data.name == 'array')
#
#        lmd_root = loaded_data.root.metadata['metadata_root']
#        lmd_root2 = loaded_data.root.metadata['metadata_root2']
#        lar = loaded_data
#        lmd = lar.metadata['metadata']
#        lmd2 = lar.metadata['metadata2']
#        lpl5 = loaded_data.tree('pointlist5')
#
#        # Ensure the data that shouldn't be here, isn't
#        assert('pointlist3' not in loaded_data.root._branch.keys())
#        assert('array' in loaded_data.root._branch.keys())
#
#        # Check types
#        assert(isinstance(lmd_root,Metadata))
#        assert(isinstance(lmd_root2,Metadata))
#        assert(isinstance(lar,Array))
#        assert(isinstance(lmd,Metadata))
#        assert(isinstance(lmd2,Metadata))
#        assert(isinstance(lpl5,PointList))
#
#        # New objects are distinct from old objects
#        assert(lmd_root is not self.md_root)
#        assert(lmd_root2 is not self.md_root2)
#        assert(lar is not self.ar)
#        assert(lmd is not self.md)
#        assert(lmd2 is not self.md2)
#        assert(lpl5 is not self.pl5)
#
#        # New objects carry identical data to old objects
#        assert(lmd_root._params == self.md_root._params)
#        assert(lmd_root2._params == self.md_root2._params)
#        assert(array_equal(lar.data, self.ar.data))
#        assert(not(array_equal(lar.data, self.ar2.data))) # ensure we didn't overwrite
#        assert(lmd._params == self.md._params)
#        assert(lmd2._params == self.md2._params)
#        assert(self.pointlist_equal(lpl5, self.pl5))
#
#        pass
#
#
#    def test_append_over_io(self):
#        """ Tree should be
#                root
#                    |--array
#                        |--pointlist5
#        where array should have no metadata and its data should
#        be that of ar2 and not ar1
#        """
#        # Load data
#        loaded_data = read(
#            subtree_append_over_path
#        )
#
#        # Does the tree look as it should?
#        assert(isinstance(loaded_data,Array))
#        assert(loaded_data.name == 'array')
#
#        lmd_root = loaded_data.root.metadata['metadata_root']
#        lmd_root2 = loaded_data.root.metadata['metadata_root2']
#        assert(len(loaded_data.metadata)==0)
#        lpl5 = loaded_data.tree('pointlist5')
#
#        # Ensure the data that shouldn't be here, isn't
#        assert('pointlist3' not in loaded_data.root._branch.keys())
#        assert('array' in loaded_data.root._branch.keys())
#
#        # Check types
#        assert(isinstance(lmd_root,Metadata))
#        assert(isinstance(lmd_root2,Metadata))
#        assert(isinstance(lpl5,PointList))
#
#        # New objects are distinct from old objects
#        assert(lmd_root is not self.md_root)
#        assert(lmd_root2 is not self.md_root2)
#        assert(loaded_data is not self.ar2)
#        assert(lpl5 is not self.pl5)
#
#        # New objects carry identical data to old objects
#        assert(lmd_root._params == self.md_root._params)
#        assert(lmd_root2._params == self.md_root2._params)
#        assert(array_equal(loaded_data.data, self.ar2.data))    # ensure we did overwrite
#        assert(not(array_equal(loaded_data.data, self.ar.data)))
#        assert(self.pointlist_equal(lpl5, self.pl5))
#
#        pass
#
#
#
#
#
#
#    # setup/teardown utilities
#
#    def _write_h5_single_node(self):
#        """
#        Write a single node to file
#        """
#        save(
#            single_node_path,
#            self.ar,
#            tree = False
#        )
#
#    def _write_h5_unrooted_node(self):
#        """
#        Write an unrooted node to file
#        """
#        save(
#            unrooted_node_path,
#            self.ar_unrooted
#        )
#
#    def _write_h5_whole_tree(self):
#        """
#        Write the whole tree to file
#        """
#        save(
#            whole_tree_path,
#            self.root,
#            tree = True
#        )
#
#    def _write_h5_subtree(self):
#        """
#        Write a subtree to file
#        """
#        save(
#            subtree_path,
#            self.pl3,
#            tree = True
#        )
#
#    def _write_h5_subtree_noroot(self):
#        """
#        Write a subtree tree to file without it's root dataset
#        """
#        save(
#            subtree_noroot_path,
#            self.pl3,
#            tree = None
#        )
#
#    def _append_to_h5(self):
#        """
#        Append to an existing h5 file
#        """
#        save(
#            subtree_append_to_path,
#            self.ar,
#            tree = False
#        )
#        save(
#            subtree_append_to_path,
#            self.ar2,
#            tree = True,
#            mode = 'a'
#        )
#        pass
#
#    def _append_over_h5(self):
#        """
#        Append to an existing h5 file, overwriting a redundantly named object
#        """
#        save(
#            subtree_append_over_path,
#            self.ar,
#            tree = False
#        )
#        save(
#            subtree_append_over_path,
#            self.ar2.root,
#            tree = True,
#            mode = 'ao'
#        )
#        pass
#
#    def _clear_files(self):
#        """
#        Delete h5 files which this test suite wrote
#        """
#        paths = [
#            single_node_path,
#            unrooted_node_path,
#            whole_tree_path,
#            subtree_path,
#            subtree_noroot_path,
#            subtree_append_to_path,
#            subtree_append_over_path
#        ]
#        for p in paths:
#            if exists(p):
#                remove(p)
#
#
#
#
#
#
