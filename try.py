import streamlit as st
import os
from PIL import Image
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



# def extract_coordinates(image_path):
    # # Open the image
    # img = Image.open(image_path)

    # # Extract EXIF metadata
    # exif_data = img._getexif()
    
    # latitude_dd = None
    # longitude_dd = None
    
    # for tag, value in exif_data.items():
    #     tag_name = TAGS.get(tag, tag)
    #     if tag_name == 'GPSInfo':
    #         # Extract GPS information
    #         for gps_tag in value:
    #             gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
    #             gps_value = value[gps_tag]
                
    #             # Convert DMS to DD for latitude and longitude
    #             if gps_tag_name == 'GPSLatitude':
    #                 latitude_dd = dms_to_dd(gps_value)
    #             elif gps_tag_name == 'GPSLongitude':
    #                 longitude_dd = dms_to_dd(gps_value)
    
    # return latitude_dd, longitude_dd


def main():
    st.title("Photo GPS Coordinates Finder")

    # Sidebar for user input
    st.sidebar.header("User Input")
    input_latitude = st.sidebar.number_input("Enter latitude in degrees:")
    input_longitude = st.sidebar.number_input("Enter longitude in degrees:")

    # Folder upload
    uploaded_folder = st.sidebar.file_uploader("Upload a folder of images", type=["zip"], accept_multiple_files=False)

    # User-specified destination folder
    destination_folder = st.sidebar.text_input("Enter the destination folder path:")


    if uploaded_folder:
      
        # Handle the uploaded folder of images
        st.header("Matching Photos for Uploaded Folder")

        with st.spinner("Processing..."):
            folder_name = os.path.basename(uploaded_folder.name)
            path = "/home/rubi/Desktop"
            folder_path = os.path.join(path, folder_name)

            print ("path is:\n\n\n",folder_path)    


            # Save the uploaded ZIP folder and extract its contents
            # os.makedirs(folder_path, exist_ok=True)
            # with open(os.path.join(folder_path, folder_name), "wb") as folder_file:
            #     folder_file.write(uploaded_folder.read())
            # shutil.unpack_archive(os.path.join(folder_path, folder_name), extract_dir=folder_path)

            with zipfile.ZipFile(folder_path, "r") as zip_ref:
                zip_ref.extractall(path)
            print ("\n\ntala ko path is:\n\n\n",folder_path)
            image_file= glob.glob(f"{path}/new/*.JPG", recursive=True)


            print ("\n\ntala ko path is:\n\n\n",image_file)

            matching_photos = []
            for filename in image_file:
                image_path = os.path.join(folder_path, filename)
                print ("image path is:\n\n\n",image_path)
                photo_latitude, photo_longitude = extract_coordinates(image_path)

                if photo_latitude is not None and photo_longitude is not None:
                    distance = geodesic((input_latitude, input_longitude), (photo_latitude, photo_longitude)).meters

                    if distance < 100:
                        matching_photos.append(filename)
                        copy_matching_photo(image_path, destination_folder)

            if matching_photos:
                st.success(f"Found {len(matching_photos)} matching photos in the folder.")
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