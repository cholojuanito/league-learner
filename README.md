# league-learner
Machine Learning project applied to League of Legends

# Setup

## Anaconda
This project makes use of Anaconda and runs according to the `env.yml` file to create the Anaconda environment. You can change this file or update your environment if you need to.
1. Make sure you have Anaconda installed on your machine.
2. Clone this repo
3. Make sure you are in the correct working directory then run the following in the command line:
    ```
    conda env create -f env.yml
    ```
4. Start the environment
    ```
    conda activate league
    ```

## Environment Variables
In order to access Riot Games' API you will need an API key. You can get one [here](https://developer.riotgames.com/). Unless you have a dedicated application that has been approved by Riot, you will experience a limit to the number of requests you can do on a per second and per minute basis. The package [Cassiopeia](https://github.com/meraki-analytics/cassiopeia) that is installed with the Anaconda environment should take care of these limits.

To be secure, we assume that your API key will be stored as an environment variable. We also did this because if you don't have an application approved with Riot you will need to change this variable everyday. 

To change or add this variable to your Anaconda environment run this command:
```
conda env config vars set RIOT_API_KEY=RGAPI<YOUR_API_KEY>
```
Then to make sure that this variable has been set run:
```
conda env config vars list
```
And you should see your new environment variable in the list.