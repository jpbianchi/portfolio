#%%writefile /content/podcast/podcast_backend_trans_all3.py
import modal

def download_whisper():
  # Load the Whisper model
  import os
  import whisper
  print ("Download the Whisper model")

  # Perform download only once and save to Container storage
  whisper._download(whisper._MODELS["medium"], '/content/podcast/', False)


stub = modal.Stub("corise-podcast-project")
corise_image = modal.Image.debian_slim().pip_install("feedparser",
                                                     "https://github.com/openai/whisper/archive/9f70a352f9f8630ab3aa0d06af5cb9532bd8c21d.tar.gz",
                                                     "requests",
                                                     "ffmpeg",
                                                     "openai",
                                                     "tiktoken",
                                                     "wikipedia",
                                                     "ffmpeg-python").apt_install("ffmpeg").run_function(download_whisper)

@stub.function(image=corise_image, gpu="A100", timeout=1200)
def get_transcribe_podcast(rss_url, local_path):
  print ("Starting Podcast Transcription Function")
  print ("Feed URL: ", rss_url)
  print ("Local Path:", local_path)

  # Read from the RSS Feed URL
  import feedparser
  intelligence_feed = feedparser.parse(rss_url)
  if isinstance(intelligence_feed['feed'], dict) and 'title' in intelligence_feed['feed']:
    # in case a user gives a link to a bad RSS feed, or no feed at all
    podcast_title = intelligence_feed['feed']['title']
  else: 
    return None
  
  episode_title = intelligence_feed.entries[0]['title']
  episode_image = intelligence_feed['feed']['image'].href
  for item in intelligence_feed.entries[0].links:
    if (item['type'] == 'audio/mpeg'):
      episode_url = item.href
  episode_name = "podcast_episode.mp3"
  print ("RSS URL read and episode URL: ", episode_url)

  # Download the podcast episode by parsing the RSS feed
  from pathlib import Path
  p = Path(local_path)
  p.mkdir(exist_ok=True)

  print ("Downloading the podcast episode")
  import requests
  with requests.get(episode_url, stream=True) as r:
    r.raise_for_status()
    episode_path = p.joinpath(episode_name)
    with open(episode_path, 'wb') as f:
      for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)

  print ("Podcast Episode downloaded")

  # Load the Whisper model
  import os
  import whisper

  # Load model from saved location
  print ("Load the Whisper model")
  model = whisper.load_model('medium', device='cuda', download_root='/content/podcast/')

  # Perform the transcription
  print ("Starting podcast transcription")
  result = model.transcribe(local_path + episode_name)

  # Return the transcribed text
  print ("Podcast transcription completed, returning results...")
  output = {}
  output['podcast_title'] = podcast_title
  output['episode_title'] = episode_title
  output['episode_image'] = episode_image
  output['episode_transcript'] = result['text']
  return output

@stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"))
def get_podcast_summary(podcast_transcript):
  import openai
  ## LOGIC TO RETURN THE SUMMARY OF THE PODCAST USING OPENAI
  instructPrompt = """Please summarize the following podcast transcript in one paragraph."""

  request = instructPrompt + podcast_transcript
  chatOutput = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k",
                                     messages=[{"role": "system", "content": "You are a helpful assistant."},
                                               {"role": "user", "content": request}]
                                    )
  podcastSummary = chatOutput.choices[0].message.content
  return podcastSummary

@stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"))
def get_podcast_guest(podcast_transcript):
  import openai
  #import wikipedia
  import json
  import tiktoken
  ## LOGIC TO RETURN THE PODCAST GUEST INFORMATION
  request = podcast_transcript[:10000]
  enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
  #print ("Number of tokens in input prompt ", len(enc.encode(request)))
  completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[{"role": "user", "content": request}],
      functions=[
      {
          "name": "get_podcast_guest_information",
          "description": "Get information on the podcast guest using their full name and the name of the organization they are part of to search for them on Wikipedia or Google",
          "parameters": {
              "type": "object",
              "properties": {
                  "guest_name": {
                      "type": "string",
                      "description": "The full name of the guest who is speaking in the podcast",
                  },
                  "guest_organization": {
                      "type": "string",
                      "description": "The full name of the organization that the podcast guest belongs to or runs or works for",
                  },
                  "guest_title": {
                      "type": "string",
                      "description": "The title, designation or role of the podcast guest in their organization",
                  },
              },
              "required": ["guest_name"],
          },
      }
  ],
  function_call={"name": "get_podcast_guest_information"}
  )

  import json

  podcast_guest = ""
  podcast_guest_org = ""
  podcast_guest_title = ""

  response_message = completion["choices"][0]["message"]
  if response_message.get("function_call"):
    function_name = response_message["function_call"]["name"]
    function_args = json.loads(response_message["function_call"]["arguments"])
    podcast_guest=function_args.get("guest_name")
    print("podcast_guest extracted!")
    #podcast_guest_org=function_args.get("guest_organization")
    #podcast_guest_title=function_args.get("guest_title")
  return podcast_guest

@stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"))
def get_podcast_highlights(podcast_transcript):
  import openai
  ### LOGIC TO RETURN THE HIGHLIGHTS OF THE PODCAST
  instructPrompt = """
  Read the following text transcript of a podcast and summarize it for readers, with bullet points.
  Stick to the content, do not add comments.
  """

  request = instructPrompt + podcast_transcript
  chatOutput = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k",
                                    messages=[{"role": "system", "content": "You are a helpful assistant."},
                                              {"role": "user", "content": request}
                                              ]
                                    )
  podcastHighlights = chatOutput.choices[0].message.content
  return podcastHighlights

@stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"), timeout=1200)
def process_podcast(url, path):
  output = {}
  podcast_details = get_transcribe_podcast.remote(url, path)  # .call is deprecated
  if podcast_details is None:
    return None
  # podcast_details={'episode_transcript':"Jesse Pollack, the creator of BASE, a Layer 2 scaling solution from Coinbase, discusses the origin and value proposition of BASE in a podcast interview. BASE is an Ethereum Layer 2 incubated by Coinbase and aims to make running applications on Ethereum cheaper and more accessible. Pollack explains that the decision to build BASE as a Layer 2 rather than a new Layer 1 was driven by the belief that multiple Layer 2 solutions will be needed to scale Ethereum and bring a billion people on-chain. He highlights the importance of decentralization in BASE and outlines the roadmap for further decentralization, including the development of a neutrality framework, technical decentralization, and sustainable funding. Pollack also discusses the challenges of high transaction fees on Layer 2s and the upcoming EIP-4844 upgrade, which aims to reduce fees and increase capacity. Finally, he shares his optimistic vision of a future where a billion people are on-chain and the positive impact it can have on economic freedom and creativity."}
  
  podcast_summary = get_podcast_summary.remote(podcast_details['episode_transcript'])
  podcast_guest = get_podcast_guest.remote(podcast_details['episode_transcript'])
  podcast_highlights = get_podcast_highlights.remote(podcast_details['episode_transcript'])
  output['podcast_details'] = podcast_details
  output['podcast_summary'] = podcast_summary
  output['podcast_guest'] = podcast_guest
  output['podcast_highlights'] = podcast_highlights
  return output

@stub.local_entrypoint()
def test_method(url, path):
  output = {}
  podcast_details = get_transcribe_podcast.remote(url, path)
  print ("Podcast Summary: ", get_podcast_summary.remote(podcast_details['episode_transcript']))
  print ("Podcast Guest Information: ", get_podcast_guest.remote(podcast_details['episode_transcript']))
  print ("Podcast Highlights: ", get_podcast_highlights.remote(podcast_details['episode_transcript']))
  
  # deploy it with
  # modal token set --token-id ak-xxxxxx --token-secret as-xxxxx # given when we create a new token
  # modal deploy podcast/1/backend.py
  # View Deployment: https://modal.com/apps/jpbianchi/corise-podcast-project <<< use this project name