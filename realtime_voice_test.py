from google.cloud import speech
import pyaudio
import io

def transcribe_streaming():
    client = speech.SpeechClient()
    stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                    channels=1, rate=16000,
                                    input=True, frames_per_buffer=1024)

    audio_generator = (stream.read(1024) for _ in range(int(10 * 16000 / 1024)))  # 60秒流式处理
    requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)
    config = speech.RecognitionConfig(encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16, sample_rate_hertz=16000, language_code="en-US")
    streaming_config = speech.StreamingRecognitionConfig(config=config)
    responses = client.streaming_recognize(config=streaming_config, requests=requests)

    for response in responses:
        for result in response.results:
            print(f"Recognized Text: {result.alternatives[0].transcript}")

transcribe_streaming()
