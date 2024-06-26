# PODCAST INFO EXTRACTION WITH OPENAI

<p align="center">
  <img src="images/header.png" height="350px" width="700px"/>
</p>

This project shows how to download a podcast from a given RSS link, transcribe it into text, then process it with GPT3.5 to extract various data such as the podcast title, guest name/title/company, highlights and summary.  

It can be used to demonstrate the steps of a typical 'GPT/LLM' application, with different input data.

It was first done in a notebook (<a href="https://colab.research.google.com/drive/1TWhE6AqdwCLEdCMZAq9N8jLABX5YH4uP?usp=sharing" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open the notebook In Colab"/></a>) but you'll find it also in the repo. 
Then the backend code was upload to a GPU cluster modal.com which greatly facilitates deployment. 
The frontend was uploaded to streamlit. 


 ##### Main technologies used
 - openAI (GPT3.5-turbo)
 - whisper
 - streamlit
 - modal

##### Streamlit is an obvious choice to transfer the python frontend code from the notebook 

You can run the app on Streamlit with [this link](https://jpb-podcast-transcribe.streamlit.app).
Please don't exhaut my free GPU time, and start with the pre-loaded podcasts.

Here's the result for the Coinbase podcast about their new BASE Layer 2


<p align="center">
  <img src="images/coinbase_base.png" width="700px"/>
</p>

##### Modal provides an easy to use interface to run backend code on a GPU cloud

<p align="center">
  <img src="images/modal_backend.png" width="700px"/>
</p>

It took about 9' and 0.5\$ (modal gives \$30 of free GPU / month)

<p align="center">
  <img src="images/GPU_cost.png" height="400px" width="600px"/>
</p>
