import emdfile as emd
import numpy as np

# filepath
from os import getcwd, remove
from os.path import join, exists
path = join(getcwd(),"test.h5")



class TestListWrite():

    def setup_method(self):
        # delete the file
        if exists(path):
            remove(path)

    def teardown_method(self):
        # delete the file
        if exists(path):
            remove(path)


    # tests

    def test_two_unrooted_nodes(self):

        # make two arrays
        ar1 = emd.Array(
            data = np.array([[1,2],[3,4]]),
            name = 'an_array'
        )
        ar2 = emd.Array(
            data = np.arange(10),
            name = 'another_array'
        )

        # save them
        emd.save(
            filepath = path,
            data = [ar1,ar2],
        )

        # read them
        data = emd.read( path )

        # check
        assert(np.array_equal(data.tree('an_array').data, ar1.data))
        assert(np.array_equal(data.tree('another_array').data, ar2.data))


    def test_two_rooted_nodes(self):

        # make two arrays
        ar1 = emd.Array(
            data = np.array([[1,2],[3,4]]),
            name = 'an_array'
        )
        ar2 = emd.Array(
            data = np.arange(10),
            name = 'another_array'
        )

        # add roots
        root1 = emd.Root(name='root1')
        root2 = emd.Root(name='root2')
        root1.tree(ar1)
        root2.tree(ar2)

        # TODO - save in one go
        # save them
        #emd.save(
        #    filepath = path,
        #    data = [ar1,ar2],
        #)

        # TODO - remove
        emd.save(
            filepath = path,
            data = ar1
        )
        emd.save(
            filepath = path,
            data = ar2,
            mode = 'a'
        )

        # read them
        data1 = emd.read(
            path,
            emdpath = 'root1'
        )
        data2 = emd.read(
            path,
            emdpath = 'root2'
        )

        # check
        assert(np.array_equal(data1.data, ar1.data))
        assert(np.array_equal(data2.data, ar2.data))


    def test_two_trees(self):

        # make several arrays
        ar1 = emd.Array(
            data = np.array([[1,2],[3,4]]),
            name = 'an_array'
        )
        ar2 = emd.Array(
            data = np.arange(10),
            name = 'another_array'
        )
        ar3 = emd.Array(
            data = np.arange(6),
            name = 'array3'
        )

        # add roots
        root1 = emd.Root(name='root1')
        root2 = emd.Root(name='root2')
        root1.tree(ar1)
        root2.tree(ar2)
        root2.tree(ar3)

        # TODO - save in one go
        # save them
        #emd.save(
        #    filepath = path,
        #    data = [root1,root2],
        #)

        # TODO - remove
        emd.save(
            filepath = path,
            data = root1
        )
        emd.save(
            filepath = path,
            data = root2,
            mode = 'a'
        )

        # read them
        data1 = emd.read(
            path,
            emdpath = 'root1'
        )
        data2 = emd.read(
            path,
            emdpath = 'root2'
        )


        # check
        assert(np.array_equal(data1.data, ar1.data))
        assert(np.array_equal(data2.tree('another_array').data, ar2.data))
        assert(np.array_equal(data2.tree('array3').data, ar3.data))



    def test_mixed_list(self):
        """
        This test makes

        root1
          |--array1
          |--array2

        root2
          |--array3
          |--array4
          |--array5

        array6
        array7
        nparray
        dict

        and then calls

        emd.save(
            path,
            [
                root1,
                array3,
                array4,
                array6,
                array7,
                nparray,
                dict
            ]
        )

        which should save

        file
          |--root1
          |    |--array1
          |    |--array2
          |
          |--root2
          |    |--array3
          |    |--array4
          |
          |--root_savedlist
               |--array6
               |--array7
               |--nparray
               |--dict (metadata)

        Note that root2 should *not* contain array 5 in the saved file.
        """



        # make several arrays
        ar1 = emd.Array(
            data = np.array([[1,2],[3,4]]),
            name = 'array1'
        )
        ar2 = emd.Array(
            data = np.arange(10),
            name = 'array2'
        )
        ar3 = emd.Array(
            data = np.arange(6),
            name = 'array3'
        )
        ar4 = emd.Array(
            data = np.arange(24).reshape((2,3,4)),
            name = 'array4'
        )
        ar5 = emd.Array(
            data = np.arange(30).reshape((2,3,5)),
            name = 'array5'
        )

        # add roots
        root1 = emd.Root(name='root1')
        root1.tree(ar1)
        root1.tree(ar2)
        root2 = emd.Root(name='root2')
        root2.tree(ar3)
        root2.tree(ar4)
        root2.tree(ar5)

        # TODO - save in one go
        # save them
        #emd.save(
        #    filepath = path,
        #    data = [root1,root2],
        #)

        # TODO - remove
        emd.save(
            filepath = path,
            data = root1
        )
        emd.save(
            filepath = path,
            data = root2,
            mode = 'a'
        )

        # read them
        data1 = emd.read(
            path,
            emdpath = 'root1'
        )
        data2 = emd.read(
            path,
            emdpath = 'root2'
        )


        # check
        assert(np.array_equal(data1.data, ar1.data))
        assert(np.array_equal(data2.tree('another_array').data, ar2.data))
        assert(np.array_equal(data2.tree('array3').data, ar3.data))



