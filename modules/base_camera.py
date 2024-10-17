

class BaseCamera:
    def __init__(self, stream_url: str, neural_model: str, api_key: str):
        self.stream_url = stream_url
        self.model = get_model(model_id=neural_model, api_key=api_key)
        
    # get photo from stream
    def get_photo(self) -> numpy.ndarray:
        url = self.onboard_stream_url if is_onboard_cap else self.upper_stream_url
        jpg = self.__read_jpg_from_stream(url)
        img = cv2.imdecode(numpy.frombuffer(jpg, dtype=numpy.uint8), cv2.IMREAD_COLOR)
        return img
                    
    def __read_jpg_from_stream(self, url: str) -> bytes:
        stream = requests.get(url, stream=True)
        read_bytes = bytes()
        for chunk in stream.iter_content(chunk_size=1024):
            read_bytes += chunk
            a = read_bytes.find(b'\xff\xd8') # jpg start
            b = read_bytes.find(b'\xff\xd9') # jpg end
            if a != -1 and b != -1:
                jpg = read_bytes[a:b+2]
                # read_bytes = read_bytes[b+2:]
                return jpg
        
        stream.close()