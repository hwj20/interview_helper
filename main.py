import datetime
import tkinter as tk
from tkinter import filedialog, scrolledtext
import numpy as np
import PyPDF2
import pyaudio
import speech_recognition as sr
import openai
import threading
from openai_utils import generate_reply,determine_type
import sounddevice as sd
# 实时监听系统音频的类
# 实时监听系统音频的类
class SystemAudioListener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.listening = False
        self.sample_rate = 44100  # 采样率
        self.block_size = 2048    # 每个音频块的大小
        self.audio_buffer = []    # 用于存储音频数据

    def capture_system_audio(self, callback):
        def callback_audio(indata, frames, time, status):
            if self.listening:
                # 将音频数据添加到缓冲区中
                self.audio_buffer.extend(indata)
                # 当缓冲区音频长度足够时，处理该音频片段
                if len(self.audio_buffer) > self.sample_rate * 3:  # 设置每10秒处理一次
                    audio_data = np.concatenate(self.audio_buffer)
                    self.audio_buffer.clear()  # 清空缓冲区
                    # 播放捕获到的音频片段
                    print("playing")
                    sd.play(audio_data, self.sample_rate)
                    sd.wait()  # 等待播放完毕
                    # try:
                    #     audio_data = sr.AudioData(audio_data.tobytes(), self.sample_rate, 2)
                    #     text = self.recognizer.recognize_google(audio_data)
                    #     callback(text)
                    # except sr.UnknownValueError:
                    #     callback("音频未能识别")
                    # except sr.RequestError as e:
                    #     callback(f"请求错误: {e}")
                    # except Exception as e:
                    #     callback(f"发生错误: {e}")

        with sd.InputStream(callback=callback_audio, channels=2, samplerate=self.sample_rate, blocksize=self.block_size):
            while self.listening:
                sd.sleep(1000)  # 每隔一秒处理一次

    def start_listening(self, callback):
        self.listening = True
        threading.Thread(target=self.capture_system_audio, args=(callback,)).start()

    def stop_listening(self):
        self.listening = False
# 实时监听电脑音频的类
class MicAudioListener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.listening = False

    def listen_and_transcribe_continuously(self, callback):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.listening:
                try:
                    print("Listening...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    text = self.recognizer.recognize_google(audio)
                    callback(text)
                except sr.UnknownValueError:
                    callback("音频未能识别")
                except sr.RequestError as e:
                    callback(f"请求错误: {e}")
                except Exception as e:
                    callback(f"发生错误: {e}")

    def start_listening(self, callback):
        self.listening = True
        threading.Thread(target=self.listen_and_transcribe_continuously, args=(callback,)).start()

    def stop_listening(self):
        self.listening = False


# 读取PDF文件内容
def read_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        return ""


# 将对话记录保存到日志文件
def log_conversation(question, reply):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("conversation_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] question: {question}\n")
        log_file.write(f"[{timestamp}] answer: {reply}\n\n")

pdf_content = "Not provided"
jd ="""
Correkt is an AI startup based in Santa Barbara, California. We are looking for students currently pursuing a degree at the University of California, Santa Barbara to join us this summer as a full stack engineer intern. As a full stack engineer intern, you will work closely with the team in developing new, exciting features to our core products, and gain experience working in a modern codebase. 

This is a paid position and will continue 3 months past your start date, with opportunities for an extended term based on performance. If you do not meet the preferred qualifications, we encourage you to still apply, as we are generally looking for candidates who are highly motivated and can quickly adapt to new technologies. 

Minimum Qualifications

Must be currently pursuing a degree at the University of California, Santa Barbara.
U.S. citizen or U.S. permanent resident is NOT required for this position, however proper work authorizations will be required.
Preferred Qualifications

Proficient knowledge of full stack technologies (Django, React, Javascript, HTML, CSS).
Knowledge of Cloud based technologies: MongoDB, PostgreSQL, Google Cloud Platform, AWS.
Demonstrated ability to rapidly learn new technologies.
Strong written and verbal communication skills.
Strong problem-solving and analytical abilities.
"""

def main():

    def update_conversation_box(question, reply,role):
        if role == 0:
            conversation_box.insert(tk.END, f"Applicant: {question}\n","applicant")
        else:
            conversation_box.insert(tk.END, f"Question: {question}\n","interviewer")
            conversation_box.insert(tk.END, f"Reply: {reply}\n\n", "ai")

        # 自动滚动到底部
        conversation_box.see(tk.END)

        # 将对话记录保存到日志文件
        log_conversation(question, reply)

    def update_transcribed_text(text):
        conversation_box.insert(tk.END, f"Generating\n", "system")
        role = determine_type(text)
        role = int(role)
        if (role != 0 and role != 1):
            print("unresolved:"+text)
            return
        if role == 1:
            reply = generate_reply(question=text,cv_content=pdf_content,job_description=jd)
        else:
            reply = ""
        update_conversation_box(question=text,reply=reply,role=role)
    def start_listening():
        listener.start_listening(update_transcribed_text)

    def stop_listening():
        listener.stop_listening()

    def select_file():
        global pdf_content
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            pdf_content = read_pdf(file_path)
            # transcribed_label.config(text=f"PDF文件内容：{pdf_content}")
            print(pdf_content)
            print((len(pdf_content)))
            conversation_box.insert(tk.END, f"Upload CV Successfully\n","system")

    # 创建GUI窗口
    window = tk.Tk()
    window.title("Interview")

    # 创建 AudioListener 实例
    listener = MicAudioListener()
    # 创建对话框
    conversation_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=60, height=20)
    conversation_box.pack(pady=10)

    # 设置文本样式
    conversation_box.tag_configure("interviewer", foreground="purple")
    conversation_box.tag_configure("applicant", foreground="blue")
    conversation_box.tag_configure("ai", foreground="red")
    conversation_box.tag_configure("system", foreground="red")
    # 显示识别的文本
    # transcribed_label = tk.Label(window, text="Recognized Words", wraplength=400)
    # transcribed_label.pack(pady=10)

    # 显示OpenAI生成的回复
    reply_label = tk.Label(window, text="Generated Answer\n", wraplength=400)
    reply_label.pack(pady=10)

    # 按钮开始监听
    start_button = tk.Button(window, text="Start Listening", command=start_listening)
    start_button.pack(pady=10)

    # 按钮停止监听
    stop_button = tk.Button(window, text="End Listening", command=stop_listening)
    stop_button.pack(pady=10)

    # 按钮选择文件
    select_file_button = tk.Button(window, text="Select CV", command=select_file)
    select_file_button.pack(pady=10)

    window.mainloop()


if __name__ == "__main__":
    main()
