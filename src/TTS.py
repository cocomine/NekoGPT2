import logging
import re
from typing import Dict

import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import AudioDataStream


class TTS:
    def __init__(self, speech_key: str, speech_region: str):
        """
        Azure Text to Speech

        :param speech_key: Speech Key
        :param speech_region: Speech Region
        """
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio24Khz48KBitRateMonoMp3)
        speech_config.set_property(speechsdk.PropertyId.Speech_LogFilename, "../database/azure.log")  #debug
        speech_config.speech_synthesis_voice_name = 'zh-CN-XiaoxiaoMultilingualNeural'
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    async def text_to_speech_bytes(self, reply_json: Dict[str, str]) -> bytes:
        """
        Converts text to speech and returns the audio data as bytes.

        :param reply_json: A dictionary containing the following keys:
            - language (str): The language of the input text.
            - voice_style (str): The voice style to be used for speech synthesis.
            - normal_response (str): The input text to be converted to speech.
        :return: The synthesized speech audio data as bytes.
        """
        # insert break after '喵~' or 'meow~'
        p = re.compile(r"(喵)~(?![！。，？!,?.])")
        reply_json["normal_response"] = p.sub(r'\1~<break time="150ms"/>', reply_json["normal_response"])

        p = re.compile(r"(meow)~(?![！。，？!,?.])", re.IGNORECASE)
        reply_json["normal_response"] = p.sub(r'\1~<break time="150ms"/>', reply_json["normal_response"])

        speech_ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" xml:lang="zh-CN">
            <voice name="zh-CN-XiaoxiaoMultilingualNeural" sentenceboundarysilence-exact="300ms" commasilence-exact="200ms" tailingsilence="1s">
                <mstts:express-as style="{reply_json["voice_style"]}">
                    <prosody rate="+20.00%" pitch="+25.00%">
                        {reply_json["normal_response"]}
                    </prosody>
                </mstts:express-as>
            </voice>
        </speak>
                """

        logging.info("Synthesizing speech for text: {}".format(reply_json["normal_response"]))
        speech_synthesis_result = self.speech_synthesizer.speak_ssml_async(speech_ssml).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logging.debug("Speech synthesized for text [{}]".format(reply_json["normal_response"]))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            logging.debug("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    logging.error("Error details: {}".format(cancellation_details.error_details))
                    logging.error("Did you set the speech resource key and region values?")

        return speech_synthesis_result.audio_data

    async def text_to_speech_file(self, reply_json: Dict[str, str], file_name: str) -> None:

        #insert break after '喵~' or 'meow~'
        p = re.compile(r"(喵)~(?![！。，？!,?.])")
        reply_json["normal_response"] = p.sub(r'\1~<break time="150ms"/>', reply_json["normal_response"])

        p = re.compile(r"(meow)~(?![！。，？!,?.])", re.IGNORECASE)
        reply_json["normal_response"] = p.sub(r'\1~<break time="150ms"/>', reply_json["normal_response"])

        speech_ssml = f"""
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" xml:lang="zh-CN">
    <voice name="zh-CN-XiaoxiaoMultilingualNeural" sentenceboundarysilence-exact="300ms" commasilence-exact="200ms" tailingsilence="1s">
        <mstts:express-as style="{reply_json["voice_style"]}">
            <prosody rate="+20.00%" pitch="+25.00%">
                {reply_json["normal_response"]}
            </prosody>
        </mstts:express-as>
    </voice>
</speak>
        """

        # Synthesize the text to speech
        logging.info("Synthesizing speech for text: {}".format(reply_json["normal_response"]))
        speech_synthesis_result = self.speech_synthesizer.speak_ssml_async(speech_ssml).get()

        # Save the synthesized audio data to a file
        audio_data_stream = AudioDataStream(speech_synthesis_result)
        audio_data_stream.save_to_wav_file(file_name)

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logging.debug("Speech synthesized for text.")
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            logging.debug("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    logging.error("Error details: {}".format(cancellation_details.error_details))
                    logging.error("Did you set the speech resource key and region values?")
