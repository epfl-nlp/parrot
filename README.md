# Parrot


<img src="parrot.png"  width="100" height="100"> &nbsp;&nbsp;&nbsp; *I repeat your questions to ChatGPT and its response back to you.*
<br><br><br>
This repo offers an educational toolkit for universities to provide their students a free and managed access to OpenAI models. Instructors can deploy this service with their own OpenAI API key and let students interact with OpenAI models through this service for free for educational purposes.

This toolkit provides the following functionalities:
- Backend API service that acts as a proxy between the user and the OpenAI API
- Python wrapper library for users to interact with the backend service
- Simple token-based authentication for admin and user access
- Tracking of user interactions with OpenAI models in an SQL database
- Handling of budgeted access based on number of tokens used in interactions
- Retry with linear backoff strategy in case of API access failures

The toolkit has two main components: Backend Service and the Wrapper library. [backend](/backend) and [wrapper](/wrapper) folders contain the code for these components respectively. In each folder, you can find instructions on how to deploy and use these components. Feel free to fork this repo and customize to your needs. This software is licensed under [MIT License](https://opensource.org/license/mit/).

## Citation
If you use this software please consider citing it:
<pre>
@software{epflnlpparrot,
  author       = {Mete Ismayilzada and
                  Antoine Bosselut},
  title        = {EPFL NLP Parrot},
  year         = 2023,
  url          = {https://github.com/epfl-nlp/parrot}
}
</pre>