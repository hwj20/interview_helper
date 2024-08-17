import sounddevice as sd

# 列出所有设备
devices = sd.query_devices()
print(devices)

# 假设我们选择了 "Stereo Mix" 或虚拟音频设备，并找到它的索引
input_device_index = 8  # 需要替换为你查询到的设备索引
# device_info = sd.query_devices(input_device_index, 'input')

# 获取设备支持的输入通道数
# input_channels = device_info['max_input_channels']

# 设置采样率和块大小
sample_rate = 44100
block_size = 4096

# 确保通道数是设备支持的
# print(f"设备支持的最大输入通道数: {input_channels}")

# 开始捕获系统音频并播放
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    # 播放捕获到的音频数据
    sd.play(indata, sample_rate)
    sd.wait()

try:
    # 开始录制并实时播放音频，使用动态检测的通道数
    with sd.InputStream(device=input_device_index, channels=8, samplerate=sample_rate, blocksize=block_size, callback=audio_callback):
        print("开始捕获系统音频，并实时播放...")
        sd.sleep(10000)  # 设置录制持续时间为10秒（可调整）
except Exception as e:
    print(f"捕获音频时出错: {e}")
