import io
import json

import boto3
import streamlit as st
from PIL import Image, ImageDraw, ImageOps
from pydantic import BaseSettings
from urlextract import URLExtract

st.set_page_config(
    page_title="URL Scan",
    page_icon=":computer:",
    layout="wide",
)


class Settings(BaseSettings):
    """Handles fetching configuration from environment variables and secrets.
    Type-hinting for config as a bonus"""

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str


settings = Settings()

rekog_client = boto3.client(
    "rekognition",
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)
extractor = URLExtract()
extractor.update()


def compress_pil_image(image: Image, limit=(5 * (2 ** 20))) -> bytes:
    """Takes a Pillow image and returns byte values of the image saved as png.
    Reduces dimensions of image if it is larger than provided limit.

    Args:
        image (Image): Image to get the bytes for
        limit (int, optional): Maximum number of bytes. Defaults to 5mb (5 * (2 ** 20)).

    Returns:
        bytes: image saved as PNG bytes object
    """
    image_bytes = io.BytesIO()
    image.save(image_bytes, "PNG")
    output = image_bytes.getvalue()

    limit_to_bytes_ratio = limit / len(output)

    if limit_to_bytes_ratio >= 1.0:
        return output
    else:
        st.warning(f"Resizing by ratio: {limit_to_bytes_ratio}")
        width, height = image.size
        new_width = int(width * limit_to_bytes_ratio)
        new_height = int(height * limit_to_bytes_ratio)
        new_image = image.resize((new_width, new_height), Image.ANTIALIAS)
        return compress_pil_image(new_image, limit)


def rekog_detect_by_bytes(image_bytes: bytes) -> dict:
    """Takes an array of bytes representing jpg / png image.
    Tries to return response from AWS Rekognition detect_text API on the image bytes
    See docs for more: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html#Rekognition.Client.detect_text  # noqa: E501

    Args:
        image_bytes (bytes): Image to run detection on (less than 5 mb)

    Returns:
        dict: List of text detections, geometry of the detections, and metadata
    """
    response = rekog_client.detect_text(Image={"Bytes": image_bytes})
    return response


def url_with_protocol(raw_url: str, protocol: str = "http://") -> str:
    if raw_url.startswith("http"):
        return raw_url
    else:
        return protocol + raw_url


def main():
    """Main Streamlit App Entrypoint"""
    st.title("URL Scan :computer:")
    st.header(
        "Never type a URL from real life again!"
        "Upload an image and we'll scan any links so you can click them!"
    )

    uploaded_bytes = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg"],
    )

    if uploaded_bytes is not None:
        with st.spinner("Getting Image Bytes"):
            image_obj = Image.open(uploaded_bytes)
            # Handle rotations if necessary
            image_obj = ImageOps.exif_transpose(image_obj)
            image_w, image_h = image_obj.size
            # Get bytes and compress to 5 mb if needed
            image_bytes = compress_pil_image(image_obj)

        with st.spinner("Detecting Text in the image"):
            response = rekog_detect_by_bytes(image_bytes)
            extracted_text = []

            painted_image = image_obj.copy()
            canvas = ImageDraw.Draw(painted_image)
            for detection in response["TextDetections"]:
                if detection["Type"] == "LINE":
                    text = detection["DetectedText"]
                    extracted_text.append(text)
                    aws_bbox = detection["Geometry"]["BoundingBox"]
                    top_left_x = aws_bbox["Left"] * image_w
                    top_left_y = aws_bbox["Top"] * image_h
                    box_width = aws_bbox["Width"] * image_w
                    box_height = aws_bbox["Height"] * image_h
                    bot_right_x = top_left_x + box_width
                    bot_right_y = top_left_y + box_height
                    canvas.rectangle(
                        (top_left_x, top_left_y, bot_right_x, bot_right_y),
                        outline="Red",
                        width=3,
                    )
            extracted_urls = extractor.find_urls(" ".join(extracted_text))
        st.success(
            f"Found {len(extracted_urls)} URLs in {len(extracted_text)} Lines of text!"
        )

        col1, col2 = st.columns(2)
        col1.header("Detected Text Boxes")
        col1.image(
            painted_image,
            use_column_width=True,
        )

        col2.header("Extracted URLs")
        for url in extracted_urls:
            col2.write(f"- [{url}]({url_with_protocol(url)})")

        extracted_url_data = json.dumps(extracted_urls, indent=4, ensure_ascii=True)
        col2.download_button(
            label="Download extracted url list",
            data=extracted_url_data,
            file_name="extracted_urls.json",
            mime="text/json",
        )
        col2.header("Extracted Lines of Text")
        col2.write(extracted_text)

        extracted_text_data = json.dumps(extracted_text, indent=4, ensure_ascii=True)
        col2.download_button(
            label="Download all extracted text lines",
            data=extracted_text_data,
            file_name="extracted_text.json",
            mime="text/json",
        )

        with st.expander("Show Raw Image and Response", expanded=False):
            st.header("Raw Image")
            st.image(
                image_obj,
                use_column_width=True,
            )

            st.header("Raw response")
            st.write(response)


if __name__ == "__main__":
    main()
