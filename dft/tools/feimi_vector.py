import h5py
import numpy as np

def calculate_fermi_velocity(h5_file_path):
    """
    根据 band.h5 文件计算石墨烯的费米速度。
    
    :param h5_file_path: band.h5 文件的路径
    :return: 费米速度 (m/s)
    """
    with h5py.File(h5_file_path, 'r') as f:
        # 读取数据
        fermi_energy = f['fermi_energy_eV'][()]
        band_data = f['band_data'][:]
        kpoints_frac = f['kpoints_frac_list'][:]
        rlv = f['rlv'][:]  # 3x3 矩阵，每一行是一个倒易晶格基矢
        
        # 计算 K 点的位置 (以第一个 K 点为例)
        K_point_frac = np.array([1/3, 1/3, 0])
        
        # 找到最靠近 K 点的 k 点索引
        distances = np.linalg.norm(kpoints_frac - K_point_frac, axis=1)
        K_point_index = np.argmin(distances)
        
        # 获取 K 点的笛卡尔坐标
        K_point_cart = np.dot(K_point_frac, rlv)
        
        # 获取 K 点附近 k 点的笛卡尔坐标
        kpoints_cart = np.dot(kpoints_frac, rlv)
        
        # 确定 K 点附近的索引范围
        window_size = 5
        start_index = K_point_index
        end_index = min(len(kpoints_frac), K_point_index + window_size)
        
        # 提取 K 点附近的 k 点笛卡尔坐标和能带数据
        k_near_K_cart = kpoints_cart[start_index:end_index]
        # 注意：band_data 的维度是 (能带数, k点数)
        band_near_K = band_data[:, start_index:end_index]
        
        # 检查 band_near_K 是否为空
        if band_near_K.size == 0:
            raise ValueError("No band data found near K point")
            
        # 计算相对于 K 点的波矢大小 |k - k_K|
        k_magnitude = np.linalg.norm(k_near_K_cart - K_point_cart, axis=1)
        
        # 动态选择导带（能量高于费米能级且随波矢单调增加的能带）
        # 在K点附近，导带应该是能量高于费米能级（>0）且随|k-k_K|单调增加的能带
        num_bands = band_near_K.shape[0]
        band_index_b = None
        
        # 查找满足条件的能带：能量高于费米能级且随波矢单调增加
        for i in range(num_bands):
            band_energy = band_near_K[i, :]
            # 检查能量是否都高于费米能级
            if np.all(band_energy > fermi_energy):
                break
        
        # 如果没有找到完全满足条件的能带，则查找能量随波矢单调增加且大部分为正的能带
        if band_index_b is None:
            for i in range(num_bands):
                band_energy = band_near_K[i, :]
                # 检查能量是否大部分为正
                if np.sum(band_energy > 0) >= len(band_energy) * 0.6:
                    # 检查能量是否随波矢单调增加（允许前几个点相等）
                    diff = np.diff(band_energy)
                    # 检查是否大部分差值为正（至少3/4的差值为正）
                    if np.sum(diff > 0) >= len(diff) * 0.75:
                        # 检查最后几个差值是否为正（确保总体趋势是增加的）
                        if len(diff) >= 2 and np.mean(diff[-2:]) > 0:
                            band_index_b = i
                            print(f"Warning: Using band {i} which is not strictly above Fermi level but is mostly positive and monotonically increasing")
                            break
        
        # 如果仍然没有找到合适的能带，则使用默认的能带4
        if band_index_b is None:
            band_index_b = 4
            print(f"Warning: Using default band {band_index_b}. Please verify band selection.")
            
        # 提取导带能量
        conduction_band_energy = band_near_K[band_index_b, :]
        
        # 计算费米速度
        # 使用线性拟合来计算费米速度，拟合 E = v_F * |k - k_K|
        # 进行线性拟合, 强制截距为 0
        # 使用最小二乘法拟合 y = a*x (+ 0)
        # a = (x^T * y) / (x^T * x)
        x = k_magnitude
        y = conduction_band_energy
        fermi_velocity_eV_A = np.dot(x, y) / np.dot(x, x)
        
        # 转换为 m/s
        # 费米速度是能量对波矢的导数，即 dE/dk
        # 单位是 eV/Å⁻¹ = eV·Å
        #
        # 为了将 eV·Å 转换为 m/s，我们需要:
        # 1 eV = 1.60218e-19 J
        # 1 Å = 1e-10 m
        # ħ = 1.054571817e-34 J·s
        #
        # 速度 v = (1/ħ) * (dE/dk)
        # 其中 dE/dk 的单位是 eV·Å，我们需要将其转换为 J·m。
        #
        # 1 eV·Å = 1.60218e-19 J * 1e-10 m = 1.60218e-29 J·m
        #
        # 因此，速度 v = (1/ħ) * (dE/dk) * 1.60218e-29
        #            = (dE/dk) * (1.60218e-29) / (1.054571817e-34)
        #            = (dE/dk) * 1.519e5
        
        hbar = 1.054571817e-34  # J·s
        eV_to_J = 1.60218e-19   # J/eV
        A_to_m = 1e-10          # m/Å
        
        conversion_factor = (eV_to_J * A_to_m) / hbar
        
        # 将费米速度转换为 m/s
        fermi_velocity_m_per_s = fermi_velocity_eV_A * conversion_factor
        
        return fermi_velocity_m_per_s

# 使用示例
if __name__ == "__main__":
    h5_file_path = "band.h5"
    fermi_velocity = calculate_fermi_velocity(h5_file_path)
    print(f"费米速度: {fermi_velocity} m/s")