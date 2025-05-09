# gps_extractor.py

import piexif

class GPSExtractor:
    """
    GPSExtractor extracts latitude and longitude from image EXIF metadata.
    """

    def extract_location(self, img):
        """
        Extract GPS coordinates from a PIL image if available.

        Args:
            img (PIL.Image): Image with EXIF metadata.

        Returns:
            tuple: (latitude, longitude) or (None, None) if not found.
        """
        exif_data = img.info.get('exif')
        if not exif_data:
            return None, None

        exif_dict = piexif.load(exif_data)
        gps_data = exif_dict.get('GPS')
        if not gps_data:
            return None, None

        gps_latitude = gps_data.get(piexif.GPSIFD.GPSLatitude)
        gps_latitude_ref = gps_data.get(piexif.GPSIFD.GPSLatitudeRef)
        gps_longitude = gps_data.get(piexif.GPSIFD.GPSLongitude)
        gps_longitude_ref = gps_data.get(piexif.GPSIFD.GPSLongitudeRef)

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = self._get_decimal_from_dms(
                [val[0] / val[1] for val in gps_latitude],
                gps_latitude_ref.decode()
            )
            lon = self._get_decimal_from_dms(
                [val[0] / val[1] for val in gps_longitude],
                gps_longitude_ref.decode()
            )
            return lat, lon

        return None, None

    def _get_decimal_from_dms(self, dms, ref):
        degrees, minutes, seconds = dms
        decimal = degrees + minutes / 60 + seconds / 3600
        if ref in ['S', 'W']:
            decimal = -decimal
        return decimal