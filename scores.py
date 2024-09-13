import pandas as pd

# Load the CSV file
file = pd.read_csv("results.csv")

file.columns = file.columns.str.strip()


def update_scores(new_name, new_score):
    global file

    if new_name in file['player'].values:
        player_index = file.index[file['player'] == new_name].tolist()[0]

        if new_score > file.at[player_index, 'score']:
            file.at[player_index, 'score'] = new_score
            print(f"Updated {new_name}'s score to {new_score}")
    else:
        new_entry = pd.DataFrame({'player': [new_name], 'score': [new_score]})
        file = pd.concat([file, new_entry], ignore_index=True)


    if len(file) > 10:
        file = file.sort_values(by='score', ascending=False).head(10)

    file.sort_values(by='score', ascending=False)
    file.to_csv("results.csv", index=False)

    return file

def print_scores():
    print(file)
