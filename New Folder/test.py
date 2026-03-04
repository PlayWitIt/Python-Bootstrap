#
#                    單一文件 3D 遊戲引擎與程序生成
#
#                            --- Terminus ---
#
# 這是一個完全獨立的 3D 遊戲，包含在一個 Python 文件中。無需外部資產。
# 所有圖形、紋理和聲音都是在運行時程序化生成的。
#
# 功能：
#   - 基於 NumPy 的 3D 向量和矩陣數學庫
#   - 程序化幾何體生成（立方體、球體、地形）
#   - 程序化紋理生成（使用 Perlin 噪聲）
#   - 程序化音頻合成（正弦波）
#   - 一個完整的光柵化 3D 渲染管線：
#     - 模型-視圖-投影變換
#     - 視錐裁剪（Sutherland-Hodgman 算法）
#     - 透視校正紋理映射
#     - Z-緩衝以實現正確的深度排序
#     - Lambertian 漫反射光照
#   - 第一人稱相機控制器（WASD + 滑鼠）
#   - 簡單的場景管理和遊戲對象系統
#   - 粒子系統（用於效果）
#   - 簡單的物理和碰撞檢測
#
# 依賴項：
#   - pygame
#   - numpy
#
# 說明：
#   1. 安裝依賴項：pip install pygame numpy
#   2. 運行此 Python 腳本。
#   3. 使用 WASD 移動，滑鼠環顧四周。
#   4. 按下 ESC 或關閉窗口退出。
#

import pygame
import numpy as np
import math
import random
import time
import threading
import sys
import zlib
import base64

# --- 第 1 部分：核心配置和常量 ---

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TARGET_FPS = 60

# 遊戲世界常量
WORLD_SCALE = 100.0
TERRAIN_SIZE = 2048
TERRAIN_DETAIL = 64 # 必須是 2 的冪

# 渲染常量
FIELD_OF_VIEW = math.pi / 2.0  # 90 度
Z_NEAR = 0.1
Z_FAR = 1000.0
ASPECT_RATIO = SCREEN_WIDTH / SCREEN_HEIGHT if SCREEN_WIDTH > 0 else 1.0

# 顏色常量
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_SKY = (135, 206, 235)

# --- 第 2 部分：3D 數學庫 ---
# 該庫為引擎提供所有必要的向量和矩陣運算。

# 向量函數
def vec_add(v1, v2):
    """向量加法"""
    return np.add(v1, v2)

def vec_sub(v1, v2):
    """向量減法"""
    return np.subtract(v1, v2)

def vec_mul_scalar(v, s):
    """向量與標量相乘"""
    return np.multiply(v, s)

def vec_div_scalar(v, s):
    """向量除以標量"""
    if s == 0:
        return np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)
    return np.divide(v, s)

def dot_product(v1, v2):
    """兩個向量的點積"""
    return np.dot(v1[:3], v2[:3])

def cross_product(v1, v2):
    """兩個向量的叉積"""
    return np.cross(v1[:3], v2[:3])

def vector_length(v):
    """計算向量的長度（模）"""
    return np.linalg.norm(v[:3])

def normalize_vector(v):
    """將向量歸一化為單位長度"""
    l = vector_length(v)
    if l == 0:
        return np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)
    return vec_div_scalar(v, l)

def intersect_plane(plane_p, plane_n, line_start, line_end):
    """計算線段與平面的交點"""
    plane_n = normalize_vector(plane_n)
    plane_d = -dot_product(plane_n, plane_p)
    ad = dot_product(line_start, plane_n)
    bd = dot_product(line_end, plane_n)
    t = (-plane_d - ad) / (bd - ad)
    line_start_to_end = vec_sub(line_end, line_start)
    line_to_intersect = vec_mul_scalar(line_start_to_end, t)
    return vec_add(line_start, line_to_intersect)

# 矩陣函數
def identity_matrix():
    """創建並返回一個 4x4 單位矩陣"""
    return np.identity(4, dtype=np.float32)

def translation_matrix(x, y, z):
    """創建一個平移矩陣"""
    m = identity_matrix()
    m[3, 0] = x
    m[3, 1] = y
    m[3, 2] = z
    return m

def rotation_matrix_x(angle_rad):
    """創建一個繞 X 軸的旋轉矩陣"""
    m = identity_matrix()
    m[1, 1] = math.cos(angle_rad)
    m[1, 2] = math.sin(angle_rad)
    m[2, 1] = -math.sin(angle_rad)
    m[2, 2] = math.cos(angle_rad)
    return m

def rotation_matrix_y(angle_rad):
    """創建一個繞 Y 軸的旋轉矩陣"""
    m = identity_matrix()
    m[0, 0] = math.cos(angle_rad)
    m[0, 2] = math.sin(angle_rad)
    m[2, 0] = -math.sin(angle_rad)
    m[2, 2] = math.cos(angle_rad)
    return m

def rotation_matrix_z(angle_rad):
    """創建一個繞 Z 軸的旋轉矩陣"""
    m = identity_matrix()
    m[0, 0] = math.cos(angle_rad)
    m[0, 1] = math.sin(angle_rad)
    m[1, 0] = -math.sin(angle_rad)
    m[1, 1] = math.cos(angle_rad)
    return m

def scale_matrix(x, y, z):
    """創建一個縮放矩陣"""
    m = identity_matrix()
    m[0, 0] = x
    m[1, 1] = y
    m[2, 2] = z
    return m

def projection_matrix(fov, aspect_ratio, near, far):
    """創建一個透視投影矩陣"""
    fov_rad = 1.0 / math.tan(fov * 0.5)
    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = aspect_ratio * fov_rad
    m[1, 1] = fov_rad
    m[2, 2] = far / (far - near)
    m[3, 2] = (-far * near) / (far - near)
    m[2, 3] = 1.0
    return m

def point_at_matrix(pos, target, up):
    """創建一個“look-at”矩陣，用於相機"""
    new_forward = normalize_vector(vec_sub(target, pos))
    a = vec_mul_scalar(new_forward, dot_product(up, new_forward))
    new_up = normalize_vector(vec_sub(up, a))
    new_right_3d = cross_product(new_up, new_forward)

    m = identity_matrix()
    m[0, 0:3] = new_right_3d
    m[1, 0:3] = new_up[:3]
    m[2, 0:3] = new_forward[:3]
    m[3, 0:3] = pos[:3]
    return m

def quick_inverse_matrix(m):
    """只對旋轉/平移矩陣有效的快速求逆"""
    inv = identity_matrix()
    inv[0, 0] = m[0, 0]; inv[0, 1] = m[1, 0]; inv[0, 2] = m[2, 0]
    inv[1, 0] = m[0, 1]; inv[1, 1] = m[1, 1]; inv[1, 2] = m[2, 1]
    inv[2, 0] = m[0, 2]; inv[2, 1] = m[1, 2]; inv[2, 2] = m[2, 2]
    inv[3, 0] = -(m[3, 0] * inv[0, 0] + m[3, 1] * inv[1, 0] + m[3, 2] * inv[2, 0])
    inv[3, 1] = -(m[3, 0] * inv[0, 1] + m[3, 1] * inv[1, 1] + m[3, 2] * inv[2, 1])
    inv[3, 2] = -(m[3, 0] * inv[0, 2] + m[3, 1] * inv[1, 2] + m[3, 2] * inv[2, 2])
    return inv

def multiply_matrix_vector(m, v):
    """矩陣與向量相乘"""
    res = np.dot(v, m) # Using v @ m for row vectors, assuming matrices are transposed from typical column-vector math
    if res[3] != 0.0:
        res /= res[3]
    return res

# --- 第 3 部分：程序化資產生成 ---

# Perlin 噪聲生成器
class PerlinNoise:
    """一個用於生成 Perlin 噪聲的類，用於程序化紋理和地形。"""
    def __init__(self, seed=None):
        if seed is None:
            seed = random.randint(0, 255)
        self.p = np.arange(256, dtype=int)
        np.random.seed(seed)
        np.random.shuffle(self.p)
        self.p = np.stack([self.p, self.p]).flatten()

    def fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(self, t, a, b):
        return a + t * (b - a)

    def grad(self, hash, x, y, z):
        h = hash & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h in (12, 14) else z)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

    def noise(self, x, y=0, z=0):
        X = int(np.floor(x)) & 255
        Y = int(np.floor(y)) & 255
        Z = int(np.floor(z)) & 255

        x -= np.floor(x)
        y -= np.floor(y)
        z -= np.floor(z)

        u = self.fade(x)
        v = self.fade(y)
        w = self.fade(z)

        p = self.p
        A = p[X] + Y; AA = p[A] + Z; AB = p[A + 1] + Z
        B = p[X + 1] + Y; BA = p[B] + Z; BB = p[B + 1] + Z

        return self.lerp(w, self.lerp(v, self.lerp(u, self.grad(p[AA], x, y, z),
                                                self.grad(p[BA], x - 1, y, z)),
                                      self.lerp(u, self.grad(p[AB], x, y - 1, z),
                                                self.grad(p[BB], x - 1, y - 1, z))),
                         self.lerp(v, self.lerp(u, self.grad(p[AA + 1], x, y, z - 1),
                                                self.grad(p[BA + 1], x - 1, y, z - 1)),
                                  self.lerp(u, self.grad(p[AB + 1], x, y - 1, z - 1),
                                            self.grad(p[BB + 1], x - 1, y - 1, z - 1))))

    def fractional_brownian_motion(self, x, y, z, octaves, persistence):
        """使用多個八度疊加噪聲以創建更複雜的模式"""
        total = 0
        frequency = 1
        amplitude = 1
        max_value = 0
        for _ in range(octaves):
            total += self.noise(x * frequency, y * frequency, z * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2
        return total / max_value


# 紋理生成
class TextureFactory:
    """生成各種程序化紋理的工廠"""
    def __init__(self):
        self.noise_gen = PerlinNoise(seed=random.randint(0, 1000))
        self.cache = {}

    def get_texture(self, name, size=(64, 64)):
        if (name, size) in self.cache:
            return self.cache[(name, size)]

        if name == "grass":
            texture = self.create_grass_texture(size)
        elif name == "rock":
            texture = self.create_rock_texture(size)
        elif name == "water":
            texture = self.create_water_texture(size)
        elif name == "crystal":
            texture = self.create_crystal_texture(size)
        else:
            texture = self.create_default_texture(size)

        self.cache[(name, size)] = texture
        return texture

    def create_grass_texture(self, size):
        w, h = size
        surface = pygame.Surface(size)
        for y in range(h):
            for x in range(w):
                nx = x / w - 0.5
                ny = y / h - 0.5
                noise_val = self.noise_gen.fractional_brownian_motion(nx * 5, ny * 5, 0, 3, 0.5)
                noise_val = (noise_val + 1) / 2 # 映射到 0-1
                g = int(100 + noise_val * 100)
                r = int(20 + noise_val * 20)
                b = int(15 + noise_val * 15)
                surface.set_at((x, y), (np.clip(r, 0, 255), np.clip(g, 0, 255), np.clip(b, 0, 255)))
        return surface

    def create_rock_texture(self, size):
        w, h = size
        surface = pygame.Surface(size)
        for y in range(h):
            for x in range(w):
                nx = x / w
                ny = y / h
                noise_val = self.noise_gen.fractional_brownian_motion(nx * 8, ny * 8, 0, 4, 0.4)
                noise_val = (noise_val + 1) / 2
                c = int(80 + noise_val * 80)
                surface.set_at((x, y), (np.clip(c, 0, 255), np.clip(c, 0, 255), np.clip(c, 0, 255)))
        return surface

    def create_water_texture(self, size):
        w, h = size
        surface = pygame.Surface(size)
        for y in range(h):
            for x in range(w):
                nx = x / w
                ny = y / h
                noise_val = self.noise_gen.fractional_brownian_motion(nx * 10 + time.time(), ny * 10, 0, 5, 0.6)
                noise_val = (noise_val + 1) / 2
                b = int(150 + noise_val * 100)
                g = int(50 + noise_val * 50)
                r = 10
                surface.set_at((x, y), (np.clip(r, 0, 255), np.clip(g, 0, 255), np.clip(b, 0, 255)))
        return surface

    def create_crystal_texture(self, size):
        w, h = size
        surface = pygame.Surface(size, pygame.SRCALPHA)
        cx, cy = w // 2, h // 2
        for y in range(h):
            for x in range(w):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2) / (math.sqrt(cx**2 + cy**2))
                alpha = 255 * (1 - dist**2)
                r = int(150 + math.sin(dist * 20 + time.time() * 2) * 50)
                g = int(200 - dist * 100)
                b = int(230)
                surface.set_at((x, y), (np.clip(r,0,255), np.clip(g,0,255), np.clip(b,0,255), np.clip(alpha,0,255)))
        return surface


    def create_default_texture(self, size):
        w, h = size
        surface = pygame.Surface(size)
        for y in range(h):
            for x in range(w):
                if (x // 8 % 2) == (y // 8 % 2):
                    surface.set_at((x, y), (255, 0, 255)) # 洋紅色
                else:
                    surface.set_at((x, y), (0, 0, 0)) # 黑色
        return surface

# 聲音生成
class SoundFactory:
    """生成程序化音效的工廠"""
    def __init__(self, sample_rate=44100, bits=16):
        pygame.mixer.pre_init(sample_rate, -bits, 2)
        pygame.mixer.init()
        self.sample_rate = sample_rate
        self.bits = bits
        self.cache = {}

    def get_sound(self, name):
        if name in self.cache:
            return self.cache[name]

        if name == "collect":
            sound = self.create_collect_sound()
        elif name == "footstep":
            sound = self.create_footstep_sound()
        else:
            return None

        self.cache[name] = sound
        return sound

    def generate_wave(self, freq, duration_ms, wave_type='sine'):
        """生成 PCM 波形數據"""
        num_samples = int(self.sample_rate * duration_ms / 1000.0)
        max_amplitude = 2**(self.bits - 1) - 1

        buf = np.zeros((num_samples, 2), dtype=np.int16)

        for i in range(num_samples):
            t = float(i) / self.sample_rate

            if wave_type == 'sine':
                val = math.sin(2.0 * math.pi * freq * t)
            elif wave_type == 'square':
                val = 1 if math.sin(2.0 * math.pi * freq * t) > 0 else -1
            else: # saw
                val = (2.0 * (t * freq - math.floor(0.5 + t * freq)))

            # 應用簡單的 ADSR 包絡
            attack_time = 0.01
            decay_time = 0.1
            sustain_level = 0.7
            release_time = 0.1
            total_time = duration_ms / 1000.0

            if t < attack_time:
                envelope = t / attack_time
            elif t < attack_time + decay_time:
                envelope = 1.0 - (1.0 - sustain_level) * (t - attack_time) / decay_time
            elif t > total_time - release_time:
                 envelope = sustain_level * (total_time - t) / release_time
            else:
                envelope = sustain_level

            sample = int(max_amplitude * val * envelope)
            buf[i][0] = sample # 左聲道
            buf[i][1] = sample # 右聲道

        return pygame.sndarray.make_sound(buf)

    def create_collect_sound(self):
        sound = self.generate_wave(880, 200, 'sine')
        return sound

    def create_footstep_sound(self):
        # 腳步聲更像是噪音，但我們用低頻正弦波模擬
        sound = self.generate_wave(120, 150, 'saw')
        sound.set_volume(0.4)
        return sound

# --- 第 4 部分：渲染引擎核心 ---

class Mesh:
    """存儲 3D 模型數據的類，包括頂點、面和材質"""
    def __init__(self, name="default"):
        self.name = name
        self.vertices = np.array([], dtype=np.float32)
        self.tex_coords = np.array([], dtype=np.float32)
        self.faces = np.array([], dtype=np.int32)
        self.texture = None
        self.normals = np.array([], dtype=np.float32)

    def calculate_normals(self):
        """為網格的每個面計算法線"""
        self.normals = np.zeros_like(self.vertices)
        for face in self.faces:
            v0_idx, v1_idx, v2_idx = face[:, 0]

            v0 = self.vertices[v0_idx]
            v1 = self.vertices[v1_idx]
            v2 = self.vertices[v2_idx]

            line1 = vec_sub(v1, v0)
            line2 = vec_sub(v2, v0)

            normal_3d = cross_product(line1, line2)
            normal = normalize_vector(np.append(normal_3d, 0))

            self.normals[v0_idx] = vec_add(self.normals[v0_idx], normal)
            self.normals[v1_idx] = vec_add(self.normals[v1_idx], normal)
            self.normals[v2_idx] = vec_add(self.normals[v2_idx], normal)

        for i in range(len(self.normals)):
            self.normals[i] = normalize_vector(self.normals[i])


class MeshFactory:
    """生成各種程序化 3D 網格的工廠"""
    def __init__(self, texture_factory):
        self.texture_factory = texture_factory
        self.noise_gen = PerlinNoise(seed=random.randint(0,1000))
        self.cache = {}

    def get_mesh(self, name):
        if name in self.cache:
            return self.cache[name]

        if name == "cube":
            mesh = self.create_cube()
        elif name == "terrain":
            mesh = self.create_terrain()
        elif name == "crystal":
            mesh = self.create_crystal()
        else:
            return None

        mesh.calculate_normals()
        self.cache[name] = mesh
        return mesh

    def create_cube(self):
        m = Mesh("cube")
        m.vertices = np.array([
            [-0.5, -0.5, -0.5, 1], [0.5, -0.5, -0.5, 1], [0.5, 0.5, -0.5, 1], [-0.5, 0.5, -0.5, 1],
            [-0.5, -0.5, 0.5, 1], [0.5, -0.5, 0.5, 1], [0.5, 0.5, 0.5, 1], [-0.5, 0.5, 0.5, 1]
        ], dtype=np.float32)

        m.tex_coords = np.array([
            [0, 1], [1, 1], [1, 0], [0, 0]
        ], dtype=np.float32)

        m.faces = np.array([
            # (頂點索引, 紋理坐標索引)
            # 前
            [0, 0], [1, 1], [2, 2], [0, 0], [2, 2], [3, 3],
            # 後
            [4, 0], [7, 3], [6, 2], [4, 0], [6, 2], [5, 1],
            # 左
            [4, 0], [0, 1], [3, 2], [4, 0], [3, 2], [7, 3],
            # 右
            [1, 1], [5, 0], [6, 3], [1, 1], [6, 3], [2, 2],
            # 上
            [3, 0], [2, 1], [6, 2], [3, 0], [6, 2], [7, 3],
            # 下
            [4, 3], [5, 2], [1, 1], [4, 3], [1, 1], [0, 0],
        ], dtype=np.int32).reshape(-1, 3, 2)

        m.texture = self.texture_factory.get_texture("rock")
        return m

    def create_terrain(self):
        m = Mesh("terrain")
        size = TERRAIN_DETAIL
        verts = []
        tex_coords = []

        for z in range(size + 1):
            for x in range(size + 1):
                px = x / size * TERRAIN_SIZE - TERRAIN_SIZE / 2
                pz = z / size * TERRAIN_SIZE - TERRAIN_SIZE / 2

                # 使用噪聲生成高度
                nx = x / size
                nz = z / size
                height = self.noise_gen.fractional_brownian_motion(nx * 5, nz * 5, 0, 5, 0.5) * 50
                height += self.noise_gen.fractional_brownian_motion(nx * 20, nz * 20, 0, 3, 0.3) * 10

                verts.append([px, height, pz, 1.0])
                tex_coords.append([nx, nz])

        m.vertices = np.array(verts, dtype=np.float32)
        m.tex_coords = np.array(tex_coords, dtype=np.float32)

        faces = []
        for z in range(size):
            for x in range(size):
                i = z * (size + 1) + x
                # (頂點索引, 紋理坐標索引)
                # 三角形 1
                faces.extend([[i, i], [i + 1, i + 1], [i + size + 1, i + size + 1]])
                # 三角形 2
                faces.extend([[i + 1, i+1], [i + size + 2, i + size + 2], [i + size + 1, i + size + 1]])

        m.faces = np.array(faces, dtype=np.int32).reshape(-1, 3, 2)
        m.texture = self.texture_factory.get_texture("grass")
        return m

    def create_crystal(self):
        m = Mesh("crystal")

        m.vertices = np.array([
            [0, 2, 0, 1],   # 頂點
            [-1, 0, -1, 1], # 底座
            [1, 0, -1, 1],
            [1, 0, 1, 1],
            [-1, 0, 1, 1],
            [0, -1, 0, 1]  # 底部中心
        ], dtype=np.float32)

        m.tex_coords = np.array([[0.5, 0], [0, 0.5], [1, 0.5], [1, 1], [0, 1]], dtype=np.float32)

        m.faces = np.array([
            # 頂部金字塔面
            [0,0], [1,1], [2,2],
            [0,0], [2,1], [3,2],
            [0,0], [3,1], [4,2],
            [0,0], [4,1], [1,2],
            # 底部金字塔面
            [5,4], [2,2], [1,1],
            [5,4], [3,2], [2,1],
            [5,4], [4,2], [3,1],
            [5,4], [1,2], [4,1],
        ], dtype=np.int32).reshape(-1, 3, 2)

        m.texture = self.texture_factory.get_texture("crystal", size=(32,32))
        return m

class Renderer:
    """3D 渲染器類，處理所有繪圖操作"""
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.z_buffer = np.full((width, height), Z_FAR, dtype=np.float32)

        self.proj_matrix = projection_matrix(FIELD_OF_VIEW, ASPECT_RATIO, Z_NEAR, Z_FAR)

        self.light_direction = np.array([0.5, -0.8, -0.2, 0.0], dtype=np.float32)
        self.light_direction = normalize_vector(self.light_direction)

    def clear_buffers(self):
        """每幀開始時清除屏幕和 Z 緩衝區"""
        self.screen.fill(COLOR_SKY)
        self.z_buffer.fill(Z_FAR)

    def render_scene(self, scene, camera):
        """渲染場景中的所有對象"""
        view_matrix = camera.get_matrix()

        triangles_to_raster = []

        for game_object in scene.objects.values():
            if not game_object.mesh:
                continue

            world_matrix = game_object.get_world_matrix()

            # 遍歷所有面
            for face_indices in game_object.mesh.faces:
                vert_indices = face_indices[:, 0]
                tex_indices = face_indices[:, 1]

                verts = [game_object.mesh.vertices[i] for i in vert_indices]

                # Transform vertices by world matrix
                world_verts = [np.dot(v, world_matrix) for v in verts]

                # Calculate normal in world space for culling and lighting
                line1 = vec_sub(world_verts[1], world_verts[0])
                line2 = vec_sub(world_verts[2], world_verts[0])
                normal_3d = cross_product(line1, line2)
                normal = normalize_vector(np.append(normal_3d, 0))

                # Back-face culling
                vec_to_camera = vec_sub(camera.position, world_verts[0])
                if dot_product(normal, vec_to_camera) < 0.0:
                    continue

                # Lighting
                dp = max(0.1, dot_product(self.light_direction, normal))
                color = (dp * 255, dp * 255, dp * 255)

                # Transform vertices by view matrix
                viewed_verts = [np.dot(v, view_matrix) for v in world_verts]

                tex_coords = [game_object.mesh.tex_coords[i] for i in tex_indices]

                # Clip viewed triangle against near plane
                clipped_triangles = self.clip_against_plane(
                    np.array([0.0, 0.0, Z_NEAR, 1.0]),
                    np.array([0.0, 0.0, 1.0, 0.0]),
                    list(zip(viewed_verts, tex_coords))
                )

                for n in range(len(clipped_triangles)):
                    projected_verts = []
                    for i in range(3):
                        projected_v = multiply_matrix_vector(self.proj_matrix, clipped_triangles[n][i][0])

                        projected_v[0] = (projected_v[0] + 1.0) * 0.5 * self.width
                        projected_v[1] = (projected_v[1] + 1.0) * 0.5 * self.height

                        projected_verts.append(projected_v)

                    final_tex_coords = [item[1] for item in clipped_triangles[n]]

                    triangles_to_raster.append({
                        "verts": projected_verts,
                        "tex_coords": final_tex_coords,
                        "color": color,
                        "texture": game_object.mesh.texture
                    })

        for tri_data in triangles_to_raster:
            self.rasterize_triangle_textured(tri_data)


    def clip_against_plane(self, plane_p, plane_n, triangle):
        """使用 Sutherland-Hodgman 算法裁剪三角形"""
        plane_n = normalize_vector(plane_n)

        def dist(p):
            return dot_product(plane_n, vec_sub(p, plane_p))

        inside_points = []
        outside_points = []

        for p in triangle:
            if dist(p[0]) >= 0:
                inside_points.append(p)
            else:
                outside_points.append(p)

        if len(inside_points) == 0:
            return []
        if len(inside_points) == 3:
            return [triangle]

        if len(inside_points) == 1 and len(outside_points) == 2:
            in_v, in_tc = inside_points[0]
            out_v1, out_tc1 = outside_points[0]
            out_v2, out_tc2 = outside_points[1]

            d_in = dist(in_v)
            t1 = d_in / (d_in - dist(out_v1))
            intersect_p1 = vec_add(in_v, vec_mul_scalar(vec_sub(out_v1, in_v), t1))
            intersect_tc1 = in_tc + (out_tc1 - in_tc) * t1

            t2 = d_in / (d_in - dist(out_v2))
            intersect_p2 = vec_add(in_v, vec_mul_scalar(vec_sub(out_v2, in_v), t2))
            intersect_tc2 = in_tc + (out_tc2 - in_tc) * t2

            return [[(in_v, in_tc), (intersect_p1, intersect_tc1), (intersect_p2, intersect_tc2)]]

        if len(inside_points) == 2 and len(outside_points) == 1:
            in_v1, in_tc1 = inside_points[0]
            in_v2, in_tc2 = inside_points[1]
            out_v, out_tc = outside_points[0]

            d_in1 = dist(in_v1)
            t1 = d_in1 / (d_in1 - dist(out_v))
            intersect_p1 = vec_add(in_v1, vec_mul_scalar(vec_sub(out_v, in_v1), t1))
            intersect_tc1 = in_tc1 + (out_tc - in_tc1) * t1

            d_in2 = dist(in_v2)
            t2 = d_in2 / (d_in2 - dist(out_v))
            intersect_p2 = vec_add(in_v2, vec_mul_scalar(vec_sub(out_v, in_v2), t2))
            intersect_tc2 = in_tc2 + (out_tc - in_tc2) * t2

            tri1 = [(in_v1, in_tc1), (in_v2, in_tc2), (intersect_p1, intersect_tc1)]
            tri2 = [(in_v2, in_tc2), (intersect_p2, intersect_tc2), (intersect_p1, intersect_tc1)]
            return [tri1, tri2]

        return []

    def rasterize_triangle_textured(self, tri_data):
        """使用紋理和 Z-緩衝繪製一個三角形"""
        v1, v2, v3 = tri_data["verts"]
        t1, t2, t3 = tri_data["tex_coords"]
        texture = tri_data["texture"]
        light_color = tri_data["color"]

        if not texture: return
        tex_w, tex_h = texture.get_size()
        tex_pixels = pygame.surfarray.pixels3d(texture)

        # 按 y 排序頂點
        if v2[1] < v1[1]: v1, v2 = v2, v1; t1, t2 = t2, t1
        if v3[1] < v1[1]: v1, v3 = v3, v1; t1, t3 = t3, t1
        if v3[1] < v2[1]: v2, v3 = v3, v2; t2, t3 = t3, t2

        dy1 = v2[1] - v1[1]
        dy2 = v3[1] - v1[1]

        if dy1 > 0:
            for y in range(int(v1[1]), int(v2[1]) + 1):
                if y < 0 or y >= self.height: continue
                alpha = (y - v1[1]) / dy1 if dy1 != 0 else 0
                beta = (y - v1[1]) / dy2 if dy2 != 0 else 0

                ax = v1[0] + (v2[0] - v1[0]) * alpha
                bx = v1[0] + (v3[0] - v1[0]) * beta

                aw = 1/v1[2] + (1/v2[2] - 1/v1[2]) * alpha
                au = t1[0]/v1[2] + (t2[0]/v2[2] - t1[0]/v1[2]) * alpha
                av = t1[1]/v1[2] + (t2[1]/v2[2] - t1[1]/v1[2]) * alpha

                bw = 1/v1[2] + (1/v3[2] - 1/v1[2]) * beta
                bu = t1[0]/v1[2] + (t3[0]/v3[2] - t1[0]/v1[2]) * beta
                bv = t1[1]/v1[2] + (t3[1]/v3[2] - t1[1]/v1[2]) * beta

                if ax > bx: ax, bx = bx, ax; au, bu = bu, au; av, bv = bv, av; aw, bw = bw, aw
                self.draw_scanline(y, int(ax), int(bx), au, bu, av, bv, aw, bw, tex_pixels, tex_w, tex_h, light_color)

        dy1 = v3[1] - v2[1]
        dy2 = v3[1] - v1[1]

        if dy1 > 0:
            for y in range(int(v2[1]), int(v3[1]) + 1):
                if y < 0 or y >= self.height: continue
                alpha = (y - v2[1]) / dy1 if dy1 != 0 else 0
                beta = (y - v1[1]) / dy2 if dy2 != 0 else 0

                ax = v2[0] + (v3[0] - v2[0]) * alpha
                bx = v1[0] + (v3[0] - v1[0]) * beta

                aw = 1/v2[2] + (1/v3[2] - 1/v2[2]) * alpha
                au = t2[0]/v2[2] + (t3[0]/v3[2] - t2[0]/v2[2]) * alpha
                av = t2[1]/v2[2] + (t3[1]/v3[2] - t2[1]/v2[2]) * alpha

                bw = 1/v1[2] + (1/v3[2] - 1/v1[2]) * beta
                bu = t1[0]/v1[2] + (t3[0]/v3[2] - t1[0]/v1[2]) * beta
                bv = t1[1]/v1[2] + (t3[1]/v3[2] - t1[1]/v1[2]) * beta

                if ax > bx: ax, bx = bx, ax; au, bu = bu, au; av, bv = bv, av; aw, bw = bw, aw
                self.draw_scanline(y, int(ax), int(bx), au, bu, av, bv, aw, bw, tex_pixels, tex_w, tex_h, light_color)

    def draw_scanline(self, y, x1, x2, u1, u2, v1, v2, w1, w2, tex_pixels, tex_w, tex_h, light_color):
        """繪製一條水平掃描線"""
        dx = x2 - x1
        if dx == 0: return
        for x in range(max(0, x1), min(self.width, x2)):
            t = (x - x1) / dx

            one_over_w = w1 + (w2 - w1) * t

            if one_over_w > self.z_buffer[x, y]: continue
            self.z_buffer[x, y] = one_over_w

            u = (u1 + (u2 - u1) * t) / one_over_w
            v = (v1 + (v2 - v1) * t) / one_over_w

            tex_x = int(u * (tex_w - 1)) % tex_w
            tex_y = int(v * (tex_h - 1)) % tex_h

            tex_color = tex_pixels[tex_x, tex_y]
            final_color = (
                min(255, int(tex_color[0] * light_color[0] / 255)),
                min(255, int(tex_color[1] * light_color[1] / 255)),
                min(255, int(tex_color[2] * light_color[2] / 255))
            )
            self.screen.set_at((x, y), final_color)

# --- 第 5 部分：遊戲邏輯與結構 ---

class GameObject:
    """遊戲世界中對象的基類"""
    def __init__(self, name, mesh=None):
        self.name = name
        self.mesh = mesh
        self.position = np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)
        self.rotation = np.array([0.0, 0.0, 0.0], dtype=np.float32) # (yaw, pitch, roll)
        self.scale = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.velocity = np.array([0.0, 0.0, 0.0], dtype=np.float32)

    def get_world_matrix(self):
        """計算並返回此對象的世界變換矩陣"""
        trans_mat = translation_matrix(self.position[0], self.position[1], self.position[2])
        rot_x_mat = rotation_matrix_x(self.rotation[1])
        rot_y_mat = rotation_matrix_y(self.rotation[0])
        rot_z_mat = rotation_matrix_z(self.rotation[2])
        rot_mat = rot_z_mat @ rot_y_mat @ rot_x_mat
        scale_mat = scale_matrix(self.scale[0], self.scale[1], self.scale[2])

        # Combine transformations
        return scale_mat @ rot_mat @ trans_mat

    def update(self, dt):
        """更新對象的狀態"""
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        self.position[2] += self.velocity[2] * dt


class Camera(GameObject):
    """第一人稱相機"""
    def __init__(self, name, position):
        super().__init__(name)
        self.position = np.array([*position, 1.0], dtype=np.float32)
        self.up_vector = np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)
        self.yaw = math.pi # Look forward initially
        self.pitch = 0.0
        self.move_speed = 30.0
        self.rotation_speed = 1.0

    def get_matrix(self):
        """計算相機的視圖矩陣"""
        # The view matrix is the inverse of the camera's world matrix.
        # 1. Create rotation matrix from yaw and pitch
        cam_rot_y = rotation_matrix_y(self.yaw)
        cam_rot_x = rotation_matrix_x(self.pitch)
        cam_rot = cam_rot_x @ cam_rot_y

        # 2. Create translation matrix from position
        cam_translation = translation_matrix(self.position[0], self.position[1], self.position[2])

        # 3. This is the camera's world transform
        cam_world = cam_rot @ cam_translation

        # 4. The view matrix is the inverse of this
        return quick_inverse_matrix(cam_world)

    def update(self, dt):
        """根據輸入更新相機"""
        # 滑鼠控制視角
        dx, dy = pygame.mouse.get_rel()
        self.yaw += dx * self.rotation_speed * dt * 0.1
        self.pitch -= dy * self.rotation_speed * dt * 0.1
        self.pitch = np.clip(self.pitch, -math.pi/2.0 + 0.01, math.pi/2.0 - 0.01)

        # Create rotation matrix for movement based on yaw only (to move on XZ plane)
        rot_y_mat = rotation_matrix_y(self.yaw)

        forward_vec = np.dot(np.array([0.0, 0.0, 1.0, 0.0]), rot_y_mat)
        right_vec_3d = cross_product(self.up_vector, forward_vec)
        right_vec = np.append(right_vec_3d, 0)

        # 鍵盤控制移動
        keys = pygame.key.get_pressed()
        move_vec = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)

        if keys[pygame.K_w]: move_vec = vec_add(move_vec, forward_vec)
        if keys[pygame.K_s]: move_vec = vec_sub(move_vec, forward_vec)
        if keys[pygame.K_a]: move_vec = vec_sub(move_vec, right_vec)
        if keys[pygame.K_d]: move_vec = vec_add(move_vec, right_vec)

        # Normalize to prevent faster diagonal movement
        if vector_length(move_vec) > 0:
            move_vec = normalize_vector(move_vec)

        self.position = vec_add(self.position, vec_mul_scalar(move_vec, self.move_speed * dt))

class Scene:
    """管理場景中的所有遊戲對象"""
    def __init__(self):
        self.objects = {}

    def add_object(self, obj):
        self.objects[obj.name] = obj

    def get_object(self, name):
        return self.objects.get(name)

    def update(self, dt):
        for obj in self.objects.values():
            obj.update(dt)

class Particle:
    """粒子系統中的單個粒子"""
    def __init__(self, pos, vel, life, color):
        self.pos = np.array(pos, dtype=np.float32)
        self.vel = np.array(vel, dtype=np.float32)
        self.life = life
        self.max_life = life
        self.color = color

class ParticleSystem:
    """一個簡單的粒子發射器"""
    def __init__(self):
        self.particles = []
        self.max_particles = 200

    def emit(self, pos):
        if len(self.particles) < self.max_particles:
            vel = [random.uniform(-5, 5) for _ in range(3)]
            life = random.uniform(0.5, 1.5)
            color = (random.randint(200, 255), random.randint(100, 255), random.randint(100, 200))
            self.particles.append(Particle(pos, vel, life, color))

    def update(self, dt):
        for p in self.particles:
            p.life -= dt
            p.pos += p.vel * dt
            p.vel[1] -= 9.8 * dt # gravity

        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, screen, camera, proj_matrix):
        """在屏幕上繪製粒子"""
        view_matrix = camera.get_matrix()

        for p in self.particles:
            pos_4d = np.array([*p.pos, 1.0])
            viewed_pos = np.dot(pos_4d, view_matrix)

            if viewed_pos[2] > Z_NEAR:
                projected = multiply_matrix_vector(proj_matrix, viewed_pos)

                sx = (projected[0] + 1.0) * 0.5 * SCREEN_WIDTH
                sy = (projected[1] + 1.0) * 0.5 * SCREEN_HEIGHT

                if 0 < sx < SCREEN_WIDTH and 0 < sy < SCREEN_HEIGHT:
                    size = max(1, int(5 * (p.life / p.max_life)))
                    r, g, b = p.color
                    final_color = (r, g, b)
                    pygame.draw.circle(screen, final_color, (int(sx), int(sy)), size)

# --- 第 6 部分：主遊戲循環 ---

class Game:
    """主遊戲類"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Terminus Engine")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)
        self.running = True

        # 初始化工廠和渲染器
        self.texture_factory = TextureFactory()
        self.sound_factory = SoundFactory()
        self.mesh_factory = MeshFactory(self.texture_factory)
        self.renderer = Renderer(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        # 遊戲狀態
        self.score = 0
        self.collectibles = []
        self.footstep_timer = 0
        self.footstep_interval = 0.4

        self.particle_system = ParticleSystem()

        # 設置場景
        self.scene = Scene()
        self.camera = Camera("player_cam", [0, 50, -100])
        self.setup_scene()

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def setup_scene(self):
        """初始化遊戲場景，添加對象"""
        # 添加地形
        terrain_mesh = self.mesh_factory.get_mesh("terrain")
        terrain = GameObject("terrain", terrain_mesh)
        self.scene.add_object(terrain)

        # 添加可收集的水晶
        crystal_mesh = self.mesh_factory.get_mesh("crystal")
        for i in range(20):
            name = f"crystal_{i}"
            crystal = GameObject(name, crystal_mesh)

            x = random.uniform(-TERRAIN_SIZE/4, TERRAIN_SIZE/4)
            z = random.uniform(-TERRAIN_SIZE/4, TERRAIN_SIZE/4)

            # 獲取地形高度
            tx = (x + TERRAIN_SIZE/2) / TERRAIN_SIZE
            tz = (z + TERRAIN_SIZE/2) / TERRAIN_SIZE
            y = self.mesh_factory.noise_gen.fractional_brownian_motion(tx*5, tz*5, 0, 5, 0.5) * 50 + 5

            crystal.position = np.array([x, y, z, 1.0])
            crystal.scale = np.array([2.0, 2.0, 2.0])
            self.scene.add_object(crystal)
            self.collectibles.append(crystal)

    def run(self):
        """主遊戲循環"""
        while self.running:
            dt = self.clock.tick(TARGET_FPS) / 1000.0
            dt = min(dt, 0.1)

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        """處理用戶輸入和其他事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self, dt):
        """更新所有遊戲邏輯"""
        self.camera.update(dt)
        self.scene.update(dt)
        self.particle_system.update(dt)

        # 讓水晶旋轉
        for c in self.collectibles:
            c.rotation[0] += 0.5 * dt
            c.rotation[1] += 0.3 * dt

        # 碰撞檢測
        to_remove = []
        for c in self.collectibles:
            dist = vector_length(vec_sub(self.camera.position, c.position))
            if dist < 5.0:
                to_remove.append(c)
                self.score += 1
                self.sound_factory.get_sound("collect").play()
                for _ in range(50):
                    self.particle_system.emit(c.position[:3])

        # 移除收集到的物品
        for c in to_remove:
            self.collectibles.remove(c)
            del self.scene.objects[c.name]

        # 播放腳步聲
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]:
            self.footstep_timer += dt
            if self.footstep_timer > self.footstep_interval:
                self.footstep_timer = 0
                self.sound_factory.get_sound("footstep").play()


    def draw(self):
        """繪製所有內容到屏幕"""
        self.renderer.clear_buffers()
        self.renderer.render_scene(self.scene, self.camera)

        self.particle_system.draw(self.screen, self.camera, self.renderer.proj_matrix)

        self.draw_ui()

        pygame.display.flip()

    def draw_ui(self):
        """在屏幕上繪製 2D UI 元素"""
        fps_text = self.font.render(f"FPS: {self.clock.get_fps():.2f}", True, COLOR_WHITE)
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_WHITE)

        self.screen.blit(fps_text, (10, 10))
        self.screen.blit(score_text, (10, 30))

        # 準星
        crosshair_size = 10
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        pygame.draw.line(self.screen, COLOR_WHITE, (center_x - crosshair_size, center_y), (center_x + crosshair_size, center_y), 1)
        pygame.draw.line(self.screen, COLOR_WHITE, (center_x, center_y - crosshair_size), (center_x, center_y + crosshair_size), 1)


if __name__ == '__main__':
    try:
        import pygame
        import numpy
    except ImportError:
        print("錯誤：缺少依賴項。請運行 'pip install pygame numpy'")
        sys.exit(1)

    print("Terminus 引擎正在啟動...")
    print(f"分辨率: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print("控制:")
    print("  W, A, S, D: 移動")
    print("  滑鼠: 環顧四周")
    print("  ESC: 退出")
    print("---------------------------------")

    game = Game()
    game.run()
