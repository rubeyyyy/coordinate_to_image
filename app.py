import streamlit as st
import os
import streamlit as st
import os
from PIL import Image, UnidentifiedImageError  # Import UnidentifiedImageError
from PIL.ExifTags import TAGS, GPSTAGS
from fractions import Fraction
from geopy.distance import geodesic
import shutil
import zipfile
import glob


def dms_to_dd(dms):
    degrees, minutes, seconds = dms
    dd = float(Fraction(degrees) + Fraction(minutes, 60) + Fraction(seconds, 3600))
    return dd

def extract_coordinates(image_path):
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()

        latitude_dd = None
        longitude_dd = None

        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == 'GPSInfo':
                for gps_tag in value:
                    gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                    gps_value = value[gps_tag]

                    if gps_tag_name == 'GPSLatitude':
                        latitude_dd = dms_to_dd(gps_value)
                    elif gps_tag_name == 'GPSLongitude':
                        longitude_dd = dms_to_dd(gps_value)

        return latitude_dd, longitude_dd

    except UnidentifiedImageError:
        # Handle non-image files
        return None, None

def main():
    st.title("Photo GPS Coordinates Finder")

    # Sidebar for user input
    st.sidebar.header("User Input")
    input_latitude = st.sidebar.number_input("Enter latitude in degrees:",format="%.15f")
    input_longitude = st.sidebar.number_input("Enter longitude in degrees:",format="%.15f")

    # Folder upload
    uploaded_folder = st.sidebar.file_uploader("Upload a folder of images", type=["zip"], accept_multiple_files=False)

    # User-specified destination folder
    destination_folder = st.sidebar.text_input("Enter the destination folder path:")


    if uploaded_folder:
      
        # Handle the uploaded folder of images
        st.header("Matching Photos for Uploaded Folder")

        with st.spinner("Processing..."):
            folder_name = os.path.basename(uploaded_folder.name)
            folder_path = os.path.join("/tmp", folder_name)

            print ("zip path is:\n\n\n",folder_path)    

            # Save the uploaded ZIP folder
            os.makedirs(folder_path, exist_ok=True)
            with open(os.path.join(folder_path, folder_name), "wb") as folder_file:
                folder_file.write(uploaded_folder.read())


            # Extract the contents of the ZIP folder
            with zipfile.ZipFile(os.path.join(folder_path, folder_name), "r") as zip_ref:
                zip_ref.extractall(folder_path)

            print ("\n\nunzip path is:\n\n\n",folder_path)

            matching_photos = []
            for root, _, files in os.walk(folder_path):
                for filename in files:
                    image_path = os.path.join(root, filename)
                    print("image path is:\n\n\n", image_path)
                    try:
                        photo_latitude, photo_longitude = extract_coordinates(image_path)

                        if photo_latitude is not None and photo_longitude is not None:
                            distance = geodesic((input_latitude, input_longitude), (photo_latitude, photo_longitude)).meters

                            if distance < 100:
                                matching_photos.append(filename)
                                copy_matching_photo(image_path, destination_folder)
                    except UnidentifiedImageError:
                        # Handle non-image files
                        continue

            if matching_photos:
                if destination_folder:
                    st.success(f"Found {len(matching_photos)} matching photos in the folder and copied to {destination_folder}.")

                else:
                    st.warning("Please enter a destination folder path to copy matching photos.")

            else:
                    st.warning("No matching photos found in the folder.")

def copy_matching_photo(source_path, destination_folder):
    if destination_folder:
        os.makedirs(destination_folder, exist_ok=True)
        filename = os.path.basename(source_path)
        destination_path = os.path.join(destination_folder, filename)
        shutil.copy(source_path, destination_path)

if __name__ == "__main__":
    main()
    
    
    # 26.74466055913889
    # 85.92958800325