# Speech-model mirror

`silero_vad.onnx` is a byte-for-byte copy of
https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx
(Silero VAD, MIT licence, https://github.com/snakers4/silero-vad).

The Life Recorder app downloads it from GitHub first and falls back to this copy
(via jsDelivr and liferecorderapp.com) where GitHub is unreachable, e.g. mainland China.
The app checks the exact size (643,854 bytes) before using it. Never replace it with
another version: the app's VAD settings are tuned to this one.
