处理 MAPDL Full 文件 (.full)
=====================================
MAPDL full 文件是一个 FORTRAN 格式的二进制文件，包含来自 Ansys 分析的质量和刚度。使用 Pyansys 可以将其作为稀疏矩阵或全矩阵加载到内存中。


Reading a Full File
-------------------
本例读入与上例相关的质量和刚度矩阵。 ``load_km`` 对自由度进行排序，节点从最小到最大排序，每个自由度（即 X、Y、Z）在每个节点内排序。
默认情况下，矩阵 ``k`` 和 ``m`` 是稀疏的，但如果没有安装 ``scipy`` ，或者使用了可选参数 ``as_sparse=False`` ，那么它们将是完整的 numpy 数组。

默认情况下， ``load_km`` 输出两个矩阵的上三角。可以通过访问 ``fobj.const`` 来识别分析的受约束节点，其中受约束的自由度为 True ，所有其他自由度为 False 。
这与 ``dof_ref`` 中的参照度相对应。

默认情况下，dof_ref 是不排序的。要对这些值进行排序，请设置 ``sort==True`` 。本例中启用排序是为了稍后绘制数值。

.. code:: python

    from ansys.mapdl import reader as pymapdl_reader
    from ansys.mapdl.reader import examples
    
    # 创建 result reader 对象并读入 full 文件
    full = pymapdl_reader.read_binary(examples.fullfile)
    dof_ref, k, m = full.load_km(sort=True)

ANSYS 只在 full 文件中存储上三角矩阵。要创建全矩阵，请执行以下操作：

.. code:: python

    k += sparse.triu(k, 1).T
    m += sparse.triu(m, 1).T

如果安装了 ``scipy`` ，就可以求解系统的固有频率和模态振型。

.. code:: python

    import numpy as np
    from scipy.sparse import linalg

    # 对 k 矩阵进行调节，以避免出现 "因子完全奇异" 错误
    k += sparse.diags(np.random.random(k.shape[0])/1E20, shape=k.shape)

    # Solve
    w, v = linalg.eigsh(k, k=20, M=m, sigma=10000)

    # 系统自然频率
    f = (np.real(w))**0.5/(2*np.pi)    
    
.. code:: 

    print('前四阶固有频率')
    for i in range(4):
        print('{:.3f} Hz'.format(f[i]))

    前四阶固有频率
    1283.200 Hz
    1283.200 Hz

    5781.975 Hz
    6919.399 Hz


绘制模态振型
---------------------
您还可以绘制该有限元模型的模态振型。由于受约束的自由度已从解法中移除，因此在显示位移时必须考虑这些自由度。

.. code:: python
    
    import pyvista as pv

    # 获取 4 阶模态振型
    full_mode_shape = v[:, 3] # 每个节点的 x、y、z 位移
    
    # 重塑并计算归一化位移
    disp = full_mode_shape.reshape((-1, 3))
    n = (disp*disp).sum(1)**0.5
    n /= n.max() #  将数组 n 中的每个元素都除以最大值，这样 n 中的所有元素都会在 0 到 1 之间，称之为 normalize 归一化。
    
    # 加载归档文件并创建 vtk 非结构化网格
    archive = pymapdl_reader.Archive(examples.hexarchivefile)
    grid = archive.parse_vtk()
    
    # 绘制归一化位移图
    # grid.plot(scalars=n)
    
    # 绘制位移曲线
    pl = pv.Plotter()
    
    # add the nominal mesh
    pl.add_mesh(grid, style='wireframe')
	  
    # copy the mesh and displace it
    new_grid = grid.copy()
    new_grid.points += disp/80
    pl.add_mesh(new_grid, scalars=n, stitle='Normalized\nDisplacement',
                flipscalars=True)
    
    pl.add_text('Cantliver Beam 4th Mode Shape at {:.4f}'.format(f[3]),
                fontsize=30)
    pl.plot()
    
.. image:: ../images/solved_km.png


此示例内置于 ``pyansys-mapdl`` ，可通过 ``examples.solve_km()`` 运行。


FullFile 对象方法
-----------------------
.. autoclass:: ansys.mapdl.reader.full.FullFile
    :members:
