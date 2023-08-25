import streamlit as st
from pathlib import Path
import modal
import json
import os

def main():

    # cwd = os.getcwd() # it's a link to the portfolio folder (/volumes/data/dropbox.../portofolio or mnt/src/portfolio online)
    # os.chdir(cwd1) # + '/' + 'PODCAST/1')
    # cwd = os.getcwd()
    
    #st.sidebar.subheader("Debug box1")
    #st.sidebar.text_area("cwd", value=cwd, height=20)

    # the following will not work on streamlit because it starts from the repo folder
    # even if we tell it to run this backend file located in the PODCAST/1 folder
    # so pth ends up being '.'
    # if 'PORTFOLIO' in cwd:
    #     pth = cwd.split('PORTFOLIO')[1]
    # else:
    #     pth = cwd.split('portfolio')[1]
    # pth = Path(pth)    
    
    pth = 'PODCAST/1/'  
    # we must specify path to podcasts from the root since streamlit runs from the root folder, 
    # even if it can start a file in a folder
    
    #st.sidebar.subheader("Debug box2")
    #st.sidebar.text_area("pth:", value=cwd + '/' + pth, height=20)
    
    # Inject custom CSS to set the background color
    st.markdown(
        """
        <style>
       /* The main content area */
        .main .block-container {
            background-color: #206579 !important; 
            color : #fff !important;
        }

        /* The background of the entire body */
        body {
           background-color: #ec864b;
        }

         /* Applying background color to the header */
        header[data-testid="stHeader"] {
        background-color: #f7ae52 !important;
        }

        /* Your identified class from inspect element */
        .css-uf99v8 {
            display: flex;
            flex-direction: column;
            width: 100%;
            overflow: auto;
            align-items: center;
            background-color: #f7ae52;
        }

        /* Making the content and sidebar background completely opaque */
        div.stButton > button:first-child {
            background-color: #206579;
            color : #fff !important;
            border : none;
            
        }
        div[data-baseweb="select"] > div {
            background-color: #206579 ;
            color : #fff;
           
        }

        h1{
            color : #ec864b;
        }

        h2 {
            color : #7e203b
        }

        h3 {
            color : #fff
        }

        p {
            color : #fff;
        }
        
        /* Remove padding/margin from top element in the main section */
        .main .block-container:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        /* Adjust the image styling */
        stImage img {
            display: block;
            margin: 0 auto;
            padding: 0;
            border: none;
            
        }

        .css-6qob1r.e1fqkh3o3 {
        background-color: #f7ae52;
        color: #fff !important;
        }
        
        .css-6qob1r.eczjsme3{
        background-color: #f7ae52;
        color: #fff !important;
        }
        

        .sidebar.header{
        color: #206579; /* Replace with your desired color */
        }

        
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.image(pth + 'bg-image.jpg', use_column_width=True)
    
    st.title("🎙️ JPB's Favorite Podcasts!")
    
    available_podcast_info = create_dict_from_json_files(pth)

    # Left section - Input fields
    st.sidebar.header("Podcast RSS Feeds")
    
    # Dropdown box
    st.sidebar.subheader("Available Podcasts Feeds")
    selected_podcast = st.sidebar.selectbox("Select Podcast", options=available_podcast_info.keys())

    if selected_podcast:

        podcast_info = available_podcast_info[selected_podcast]

        # Right section - Newsletter content
        st.header("Your most captivating podcast right here! 🎧")

        # Display the podcast title
        st.subheader("Episode Title")
        st.write(podcast_info['podcast_details']['episode_title'])

        st.markdown("""
        <style>
            .front, .back {
            transition: transform 0.8s;
            transform-style: preserve-3d;
            backface-visibility: hidden;
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
            overflow: hidden; 
        }

        .front {
            transform: rotateY(180deg);
        }

        .back {
            transform: rotateY(0deg);
        }

        .container-rotating {
            perspective: 1000px;
            position: relative;
            width: 100%;
            height: 300px;  /* Set a fixed height */
        }

        .rotate .front {
            transform: rotateY(0deg);
        }

        .rotate .back {
            transform: rotateY(180deg);
        }

        .back img {
            width: 300px !important;  /* Set square dimensions */
            height: 300px;
            display: block;
            margin: 0 auto;
            position: absolute;  /* Center the image both vertically and horizontally */
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        </style>
        """, unsafe_allow_html=True)

    # Toggle for rotation
    rotate = st.checkbox('Display Summary', key='first-checkbox')

    rotation_class = "rotate" if rotate else ""

    st.markdown(f"""
        <div class="container-rotating {rotation_class}">
            <div class="front">
                {podcast_info['podcast_summary']}
            </div>
            <div class="back">
                <img src="{podcast_info['podcast_details']['episode_image']}" alt="Podcast Cover" style="width: 100%;">
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Display the podcast guest and their details in a side-by-side layout
    col3, col4 = st.columns([3, 7])

    with col3:
        st.subheader("Podcast Guest")
        st.write(podcast_info['podcast_guest'])

    # Display the five key moments
    st.subheader("Key Moments")
    key_moments = podcast_info['podcast_highlights']
    for moment in key_moments.split('\n'):
        st.markdown(f"<p style='margin-bottom: 5px;'>{moment}</p>", unsafe_allow_html=True)


    # User Input box
    st.sidebar.subheader("Add and Process New Podcast Feed")
    url = st.sidebar.text_input("Link to RSS Feed")

    process_button = st.sidebar.button("Process Podcast Feed")
    st.sidebar.markdown("**Note**: Podcast processing can take several minutes, please be patient.")

    if process_button:

        # Call the function to process the URLs and retrieve podcast guest information
        podcast_info = process_podcast(url)

        if podcast_info is None:
            st.header('Sorry, we could not process your podcast feed. Please try again.')
            return

        # Right section - Newsletter content
        st.header("Here's your podcast summary! 🎧")

        # Display the podcast title
        st.subheader("Episode Title")
        st.write(podcast_info['podcast_details']['episode_title'])

         # Display the podcast summary and the cover image in a side-by-side layout
        col1, col2 = st.columns([7, 3])

        with col1:
            # Display the podcast episode summary
            st.subheader("Podcast Episode Summary")
            st.write(podcast_info['podcast_summary'])

        with col2:
            st.image(podcast_info['podcast_details']['episode_image'], caption="Podcast Cover", width=300, use_column_width=True)


        # Display the podcast guest and their details in a side-by-side layout
        col3, col4 = st.columns([3, 7])

        with col3:
            st.subheader("Podcast Guest")
            if isinstance(podcast_info['podcast_guest'], dict) and 'name' in podcast_info['podcast_guest']:
                st.write(podcast_info['podcast_guest']['name'])
            else:
                st.write(podcast_info['podcast_guest'])        

        # Display the five key moments
        st.subheader("Key Moments")
        key_moments = podcast_info['podcast_highlights']
        for moment in key_moments.split('\n'):
            st.markdown(
                f"<p style='margin-bottom: 5px;'>{moment}</p>", unsafe_allow_html=True)

def create_dict_from_json_files(folder_path):
    #st.sidebar.text_area("lisdir(folder_path):", value=os.listdir(folder_path), height=50)
    json_files = [folder_path + f for f in os.listdir(folder_path) if f.endswith('.json')]
    data_dict = {}

    for file_name in json_files:
        file_path = file_name
        # st.sidebar.text_area("filename:", value=file_path, height=50)
        with open(file_path, 'r') as file:
            try:
                podcast_info = json.load(file)
                #st.sidebar.text_area("Read file correctly:", value=file_path, height=10)
            except json.JSONDecodeError:
                # the twiml AI podcast.json file was bad 
                st.sidebar.text_area("Error reading file:", value=file_path, height=10)
                continue
            podcast_name = podcast_info['podcast_details']['podcast_title']
            # Process the file data as needed
            data_dict[podcast_name] = podcast_info

    return data_dict

def process_podcast(url):
    f = modal.Function.lookup("corise-podcast-project", "process_podcast")
    output = f.remote(url, '/content/podcast/')
    return output

if __name__ == '__main__':
    main()

# get into venv and run streamlit run PODCAST/1/podcast_frontend.py --server.allowRunOnSave True
# we must run it from the root folder, not from the PODCAST/1 folder because that's what streamlit will do
# the rss link for my podcast (Coinbase L2 with Jesse Pollak) is
# https://raw.githubusercontent.com/jpbianchi/portfolio/main/PODCAST/1/anchor.fm_s_1bee9344_podcast_rss.xml?token=GHSAT0AAAAAACGBBLW7ASY24ITLP4RGT4LIZHCW4BA
# it must be created in Github, in the 'raw' mode 
# be careful, for some reason, the link to the raw file changed (despite me not changing it) so it breaks the backend since you give a link to nothing
# also, I found out a way to make google drive present a file as 'raw', by using it's FILE_ID
# get the file_id from the shareable link (1ziufPtXCLdaAkqMWsdea6uFitAYNRtax), and use it as follows
# https://drive.google.com/uc?export=download&id=1ziufPtXCLdaAkqMWsdea6uFitAYNRtax (still doesn't work... )
