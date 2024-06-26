读取 MAPDL 结果文件
==========================

Reading MAPDL Result Files

`ansys-mapdl-reader` 模块支持 MAPDL 的以下结果类型：

- ``".rfl"``
- ``".rmg"``
- ``".rst"`` - Structural analysis result file 结构分析结果文件
- ``".rth"``

MAPDL 结果文件是 FORTRAN 格式的二进制文件，包含从 MAPDL 分析写入的结果。结果至少包含分析模型的几何结构以及节点和单元结果。
根据分析，这些结果可以是从模态位移到节点温度的任何结果。这包括（但不限于）：

    - 节点自由度结果，来自静态分析或模态分析。
    - 节点自由度结果，来自循环静态或模态分析。
    - 节点平均分量应力（即 x、y、z、xy、xz、yz）
    - 节点主应力（即 S1、S2、S3、SEQV、SINT）
    - 节点弹性、塑性和热应力
    - 节点时程结果
    - 节点边界条件和力
    - 节点温度
    - 节点热应变
    - 各种单元结果（请参见 ``element_solution_data`` ）

该模块将来可能会被弃用，我们建议您查看 `DPF-Core <https://github.com/pyansys/DPF-Core>`_ 和 `DPF-Post <https://github.com/pyansys/DPF-Post>`_ 的新数据处理框架（DPF）模块，
因为它们使用客户端/服务器端接口，使用与 ANSYS Workbench 中相同的软件，但通过 Python 客户端，为 ANSYS 结果文件提供了一个更现代化的接口。


加载结果文件
-----------------------
由于 MAPDL 结果文件是二进制文件，因此无需将整个文件加载到内存中就能获取结果。该模块通过一个 python 对象 result 访问结果，您可以使用该对象 result 进行初始化：

.. code:: python

    from ansys.mapdl import reader as pymapdl_reader
    result = pymapdl_reader.read_binary('file.rst')
    
初始化时， ``Result`` 对象包含几个属性，其中包括分析的时间值、节点编号、单元编号等。

``ansys-mapdl-reader`` 模块可以通过读取 'the header of the file' 来确定正确的结果类型，
这意味着如果是 MAPDL 二进制文件， ``ansys-mapdl-reader`` 可能可以读取（至少在某种程度上）。
例如，可以使用以下命令读取热分析结果文件

.. code:: python

    rth = pymapdl_reader.read_binary('file.rth')


结果属性
-----------------
通过打印结果文件，可以快速显示 ``Result`` 的属性：

.. code:: python

    >>> result = pymapdl_reader.read_binary('file.rst')
    >>> print(result)
    PyMAPDL Result file object
    Units       : User Defined
    Version     : 20.1
    Cyclic      : False
    Result Sets : 1
    Nodes       : 321
    Elements    : 40


    Available Results:
    EMS : Miscellaneous summable items (normally includes face pressures)
    ENF : Nodal forces
    ENS : Nodal stresses
    ENG : Element energies and volume
    EEL : Nodal elastic strains
    ETH : Nodal thermal strains (includes swelling strains)
    EUL : Element euler angles
    EPT : Nodal temperatures
    NSL : Nodal displacements
    RF  : Nodal reaction forces


要获取分析的时间或频率值，请使用
    
.. code:: python

    >>> result.time_values
    array([1.])


可以使用 ``result`` 对象的多种可用方法之一获取单个结果。例如，第一个结果的节点位移可以这样用：

.. code:: python

    >>> nnum, disp = rst.nodal_displacement(0)
    >>> nnum
    array([  1,   2,   3, ..., 318, 319, 320, 321], dtype=int32)

    >>> disp
    array([[-2.03146520e-09, -3.92491045e-03,  5.00047448e-05],
           [ 1.44630651e-09,  1.17747356e-02, -1.49992672e-04],
           [ 0.00000000e+00,  0.00000000e+00,  0.00000000e+00],
           ...
           [-7.14982194e-03,  3.12495002e-03,  5.74992265e-04],
           [-7.04982329e-03,  2.44996706e-03,  5.74992939e-04],
           [-6.94982520e-03,  1.77498362e-03,  5.74992891e-04]])


可以通过以下方法获得结果的节点排序和单元编号：

.. code:: python

    >>> rst.geometry.nnum
    array([  1,   2,   3, ..., 318, 319, 320, 321], dtype=int32)

    >>> result.geometry.enum
    array([ 1,  3,  2,  4,  5,  7,  6,  8,  9, 11, 10, 12, 13, 15, 14, 16, 17,
           19, 18, 20, 21, 23, 22, 24, 25, 27, 26, 28, 29, 31, 30, 32, 33, 35,
           34, 36, 37, 39, 38, 40], dtype=int32)

Mesh
----
查询结果的 ``mesh`` 属性可找到结果的网格，该属性会返回一个 ``ansys.mapdl.reader.mesh.Mesh`` 类。

.. code:: python

    >>> from ansys.mapdl import reader as pymapdl_reader
    >>> from ansys.mapdl.reader import examples
    >>> rst = pymapdl_reader.read_binary(examples.rstfile)
    >>> print(rst.mesh)

.. code::

    ANSYS Mesh
      Number of Nodes:              321
      Number of Elements:           40
      Number of Element Types:      1
      Number of Node Components:    0
      Number of Element Components: 0


其中包含以下属性：

.. autoclass:: ansys.mapdl.reader.mesh.Mesh
    :members:


坐标系
------

非默认坐标系始终保存到 MAPDL 结果文件中。坐标系为零索引，可以通过以下方式访问各个坐标系：

.. code:: python

    >>> coord_idx = 12
    >>> result.geometry['coord systems'][coord_idx]
    {'transformation matrix': array([[ 0.0, -1.0,  0.0],
                                     [ 0.0,  0.0, -1.0],
                                     [ 1.0,  0.0,  0.0]]),
     'origin': array([0., 0., 0.]),
     'PAR1': 1.0,
     'PAR2': 1.0,
     'euler angles': array([ -0., -90.,  90.]),
     'theta singularity': 0.0,
     'phi singularity': 0.0,
     'type': 1,
     'reference num': 12}

可以通过将变换矩阵和原点连接成一个数组来构造 4x4 变换矩阵。例如：

.. code:: python

    >>> cs = result.geometry['coord systems'][coord_idx]
    >>> trans = cs['transformation matrix']
    >>> origin = cs['origin']
    >>> bottom = np.zeros(4)
    >>> bottom[3] = 1
    >>> tmat = np.hstack((trans, origin.reshape(-1 ,1)))
    >>> tmat = np.vstack((tmat, bottom))

有关结果文件中存储的坐标系内容的更多详情，请参阅 ``parse_coordinate_system`` 。


访问求解结果
--------------------------
您可以使用 ``solution_info`` 获取每个 result 的详细信息：

.. code:: python

    # 返回第一个 result 的 solution 信息字典
    info = result.solution_info(0)

    for key in info:
        print(key, info[key])


.. code:: python

    timfrq 1.0
    lfacto 1.0
    lfactn 1.0
    cptime 50.9189941460218
    tref 0.0
    tunif 0.0
    tbulk 82.0
    volbase 0.0
    tstep 0.0
    __unused 0.0
    accel_x 0.0
    accel_y 0.0
    accel_z 0.0
    omega_v_x 0.0
    omega_v_y 0.0
    omega_v_z 100
    omega_a_x 0.0
    omega_a_y 0.0
    omega_a_z 0.0
    omegacg_v_x 0.0
    omegacg_v_y 0.0
    omegacg_v_z 0.0
    omegacg_a_x 0.0
    omegacg_a_y 0.0
    omegacg_a_z 0.0
    cgcent 0.0
    fatjack 0.0
    dval1 0.0
    pCnvVal 0.0


分析中每个节点的 DOF 解可以通过下面的代码块获得。这些结果与结果文件中的节点编号相对应。该数组的大小为节点数乘以自由度数。

.. code:: python    

    # 返回结果数组（nnod x dof）, 其中 nnum 是与位移结果相对应的节点编号
    nnum, disp = result.nodal_solution(0) # 使用基于 0 的索引
    
    # 可以使用以下方法绘制相同的结果
    result.plot_nodal_solution(0, 'x', label='Displacement') # x displacement

    # normalized displacement can be plotted by excluding the direction string 通过排除方向字符串，可以绘制出归一化位移图
    result.plot_nodal_solution(0, label='Normalized')

应力也可通过以下代码获得。节点应力的计算方法与 MAPDL 相同，都是通过求取该节点上所有附加单元的应力平均值。

.. code:: python
    
    # 获得第一个结果的节点平均应力分量，每个节点有一个 [Sx, Sy Sz, Sxy, Syz, Sxz] 条目
    nnum, stress = result.nodal_stress(0) # results in a np array (nnod x 6)

    # 显示结果 6 的 X 方向节点平均应力
    result.plot_nodal_stress(5, 'Sx') # 因为 python 索引是从 0 开始的，所以这里填 `5`

    # 计算节点主应力并绘制结果 1 的 SEQV 图
    nnum, pstress = result.principal_nodal_stress(0)
    result.plot_principal_nodal_stress(0, 'SEQV')

单元应力可通过以下代码段获得。确保在 ANSYS 中对单元结果进行模态分析：

.. code:: 

    /SOLU
    MXPAND, ALL, , , YES

该代码块展示了如何访问模态分析第一个结果的非平均应力。

.. code:: python
    
    from ansys.mapdl import reader as pymapdl_reader
    result = pymapdl_reader.read_binary('file.rst')
    estress, elem, enode = result.element_stress(0)

    
这些应力可通过 MAPDL 验证：

.. code:: python

    >>> estress[0]
    [[ 1.0236604e+04 -9.2875127e+03 -4.0922625e+04 -2.3697146e+03 -1.9239732e+04  3.0364934e+03]
     [ 5.9612605e+04  2.6905924e+01 -3.6161423e+03  6.6281304e+03  3.1407712e+02  2.3195926e+04]
     [ 3.8178301e+04  1.7534495e+03 -2.5156013e+02 -6.4841372e+03 -5.0892783e+03  5.2503605e+00]
     [ 4.9787645e+04  8.7987168e+03 -2.1928742e+04 -7.3025332e+03  1.1294199e+04  4.3000205e+03]]

    >>> elem[0]
        32423

    >>> enode[0]
        array([ 9012,  7614,  9009, 10920], dtype=int32)

这与 MAPDL 的结果相同：

.. code::

  POST1:
  ESEL, S, ELEM, , 32423
  PRESOL, S

  ***** POST1 ELEMENT NODAL STRESS LISTING *****                                
 
  LOAD STEP=     1  SUBSTEP=     1                                             
   FREQ=    47.852      LOAD CASE=   0                                         
 
  THE FOLLOWING X,Y,Z VALUES ARE IN GLOBAL COORDINATES                         
 
  ELEMENT=   32423        SOLID187
    NODE    SX          SY          SZ          SXY         SYZ         SXZ     
    9012   10237.     -9287.5     -40923.     -2369.7     -19240.      3036.5    
    7614   59613.      26.906     -3616.1      6628.1      314.08      23196.    
    9009   38178.      1753.4     -251.56     -6484.1     -5089.3      5.2504    
   10920   49788.      8798.7     -21929.     -7302.5      11294.      4300.0    


从模态分析结果文件加载结果
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
本例从 ANSYS 读取梁模态分析的二进制结果。这部分代码不依赖于 ``VTK`` ，只需安装 ``numpy`` 即可使用。

.. code:: python

    # 从 pyansys 导入 reader
    from ansys.mapdl import reader as pymapdl_reader
    from ansys.mapdl.reader import examples
    
    # 结果文件示例
    rstfile = examples.rstfile
    
    # 通过加载结果文件创建结果对象
    result = pymapdl_reader.read_binary(rstfile)
    
    # 梁的固有频率
    freqs = result.time_values

.. code:: python

    >>> print(freqs)
    [ 7366.49503969  7366.49503969 11504.89523664 17285.70459456
      17285.70459457 20137.19299035]
    
获取一阶弯曲模态形状。结果根据节点编号排序。请注意，结果的索引为 0。

.. code:: python

    >>> nnum, disp = result.nodal_solution(0)
    >>> print(disp)
    [[ 2.89623914e+01 -2.82480489e+01 -3.09226692e-01]
     [ 2.89489249e+01 -2.82342416e+01  2.47536161e+01]
     [ 2.89177130e+01 -2.82745126e+01  6.05151053e+00]
     [ 2.88715048e+01 -2.82764960e+01  1.22913304e+01]
     [ 2.89221536e+01 -2.82479511e+01  1.84965333e+01]
     [ 2.89623914e+01 -2.82480489e+01  3.09226692e-01]
     ...


访问单元求解数据
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
可以使用 ``element_solution_data`` 方法访问整个求解的单元结果。例如，获取每个单元的 volume：

.. code:: python

    import numpy as np
    from ansys.mapdl import reader as pymapdl_reader

    rst = pymapdl_reader.read_binary('./file.rst')
    enum, edata = rst.element_solution_data(0, datatype='ENG')

    # 输出为列表（list），但也可视为数组（array），因为每个单元的结果大小相同
    edata = np.asarray(edata)
    volume = edata[:, 0]


模态分析求解的动画显示
~~~~~~~~~~~~~~~~~~~~~~~~~~~
使用 ``animate_nodal_solution`` 可以将模态分析的求解动画化。例如

.. code:: python

    from ansys.mapdl.reader import examples
    from ansys.mapdl import reader as pymapdl_reader

    result = pymapdl_reader.read_binary(examples.rstfile)
    result.animate_nodal_solution(3)


绘制节点结果
~~~~~~~~~~~~~~~~~~~~~~
由于模型的几何图形包含在结果文件中，因此无需加载任何其他几何图形即可绘制结果。下面是使用 ``VTK`` 绘制的模态分析梁的一阶模态位移图。

在这里，我们绘制了一阶模态 （注意索引为 0） 在 x 方向上的位移：

.. code:: python
    
    result.plot_nodal_solution(0, 'x', label='Displacement')

.. image:: ../images/hexbeam_disp.png


通过设置相机和保存结果，可以非交互式绘制结果和保存屏幕截图。这有助于批处理结果的可视化和后期处理。

首先，从交互式绘图中获取摄像机的位置：

.. code:: python

    >>> cpos = result.plot_nodal_solution(0) # 感觉这个命令好像不对啊。 ——ff
    >>> print(cpos)
    [(5.2722879880979345, 4.308737919176047, 10.467694436036483),
     (0.5, 0.5, 2.5),
     (-0.2565529433509593, 0.9227952809887077, -0.28745339908049733)]

然后生成绘图：

.. code:: python

    result.plot_nodal_solution(0, 'x', label='Displacement', cpos=cpos,
                               screenshot='hexbeam_disp.png',
                               window_size=[800, 600], interactive=False)

也可以使用下面的代码绘制应力图。节点应力的计算方法与 ANSYS 使用的方法相同，即通过求取所有附加单元在该节点处的应力平均值来确定每个节点处的应力。目前只能显示组件应力。

.. code:: python
    
    # 显示结果 6 的 X 方向节点平均应力
    result.plot_nodal_stress(5, 'Sx')

.. image:: ../images/beam_stress.png

节点应力也可通过以下非交互方式产生：

.. code:: python

    result.plot_nodal_stress(5, 'Sx', cpos=cpos, screenshot=beam_stress.png,
                             window_size=[800, 600], interactive=False)

动画模态
~~~~~~~~~~~~~~~~~~~~~~~~~~
使用 ```animate_nodal_solution`` 可将模态分析的模态振型制成动画：

.. code:: python

    result.animate_nodal_solution(0)

如果您希望将动画保存到文件中，请指定 ``movie_filename`` 参数并使用以下命令制作动画：

.. code:: python

    result.animate_nodal_solution(0, movie_filename='movie.mp4', cpos=cpos)

.. image:: ../images/beam_mode_shape.gif


循环分析的结果
------------------------------
``ansys-mapdl-reader`` 模块可以加载并显示循环分析的结果：

.. code:: python

    from ansys.mapdl import reader as pymapdl_reader

    # load the result file    
    result = pymapdl_reader.read_binary('rotor.rst')
    
您可以通过打印结果头字典键 ``'ls_table'`` 和 ``'hindex'`` 来引用荷载阶跃表和谐波索引表：

.. code:: python

    >>> print(result.resultheader['ls_table'])
    # load step, sub step, cumulative index
    array([[ 1,  1,  1], 
           [ 1,  2,  2],
           [ 1,  3,  3],
           [ 1,  4,  4],
           [ 1,  5,  5],
           [ 2,  1,  6],

    >>> print(result.resultheader['hindex'])
    array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4,
           4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7], dtype=int32)

其中每个谐波指数条目对应一个累积指数。例如，结果编号 11 是 2 次谐波指数的一阶模态：

.. code:: python

    >>> result.resultheader['ls_table'][10] # Result 11 (using zero based indexing)
    array([ 3,  1, 11], dtype=int32)
    
    >>> result.resultheader['hindex'][10]
    2

另外，也可以使用以下方法获得结果编号：

.. code:: python

    >>> mode = 1
    >>> harmonic_index = 2
    >>> result.harmonic_index_to_cumulative(mode, harmonic_index)
    24

使用这种索引方法，重复的模态由相同的模式索引进行索引。要访问另一个重复模态，请使用负谐波索引。如果结果不存在， ``ansys-mapdl-reader`` 将返回可用的模态：

.. code:: python

    >>> mode = 1
    >>> harmonic_index = 20
    >>> result.harmonic_index_to_cumulative(mode, harmonic_index)
    Exception: Invalid mode for harmonic index 1
    Available modes: [0 1 2 3 4 5 6 7 8 9]

循环分析的结果需要额外的后处理才能正确解释。模态振型作为模态解的实部和虚部的未处理部分存储在结果文件中。 ``ansys-mapdl-reader`` 将这些值合并为一个复数数组，然后返回该数组的实部结果。

.. code:: python

    >>> nnum, ms = result.nodal_solution(10) # mode shape of result 11
    >>> print(ms[:3])
    [[ 44.700, 45.953, 38.717]
     [ 42.339, 48.516, 52.475]
     [ 36.000, 33.121, 39.044]]

有时需要确定某一模态的最大位移。为此，可以用以下方法返回复数解：

.. code:: python

    nnum, ms = result.nodal_solution(0, as_complex=True)
    norm = np.abs((ms*ms).sum(1)**0.5)
    idx = np.nanargmax(norm)
    ang = np.angle(ms[idx, 0])

    # rotate the solution by the angle of the maximum nodal response
    ms *= np.cos(ang) - 1j*np.sin(ang)

    # get only the real response
    ms = np.real(ms)
    
详情请参阅 ``help(result.nodal_solution)`` 。

扇形的 real displacement 始终是模态振型 ``ms`` 的实际分量，这可以通过将模态振型乘以给定相位的复数值来改变。

使用 ``plot_nodal_solution`` 也可以显示单个扇形的结果。

.. code:: python

    rnum = result.harmonic_index_to_cumulative(0, 2)
    result.plot_nodal_solution(rnum, label='Displacement', expand=False)
    
.. image:: ../images/rotor.jpg

可以通过修改 ``phase`` 选项来改变结果的相位。有关其实现的详情，请参阅 ``help(result.plot_nodal_solution)`` 。


导出到 ParaView
---------------------
ParaView 是一种可视化应用程序，可通过图形用户界面使用 VTK 快速生成绘图和图形。 ``ansys-mapdl-reader`` 可以将 MAPDL 结果文件转换为 ParaView 兼容文件，其中包含几何和节点分析结果：

.. code:: python

    from ansys.mapdl import reader as pymapdl_reader
    from ansys.mapdl.reader import examples

    # load example beam result file
    result = pymapdl_reader.read_binary(examples.rstfile)
    
    # save as a binary vtk xml file
    result.save_as_vtk('beam.vtu') # 文件扩展名将选择要使用的写入器类型。``'.vtk'`` 将使用传统写入器，而``'.vtu'`` 将选择 VTK XML 写入器。

现在可以使用 ParaView 加载 vtk xml 文件了。该截图显示了在 `ParaView <https://www.paraview.org/>`_ 中绘制的结果文件中第一个结果的节点位移。
在 vtk 文件中，结果文件中的每个结果都有两个点数组（ ``NodalResult`` 和 ``nodal_stress`` ）。
节点结果值取决于分析类型，而节点应力始终是 Sx、Sy Sz、Sxy、Syz 和 Sxz 方向上的节点平均应力。

.. image:: ../images/paraview.jpg


结果对象方法
---------------------
.. autoclass:: ansys.mapdl.reader.rst.Result
    :members:

.. autoclass:: ansys.mapdl.reader.cyclic_reader.CyclicResult
    :members:
