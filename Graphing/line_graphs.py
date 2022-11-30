import matplotlib.pyplot as plt

def create_line_graph_alcohol_and_placebo(subid, match, variable_title, alc_data, pla_data, timepoints, yticks, ylabel, path):
    x = timepoints
    xticks = timepoints.copy()
    xticks.insert(xticks.index(30), 0)
    if -30 not in timepoints:
        xticks.insert(xticks.index(0), -30)
    plt.gca().set_xticks(xticks)
    plt.gca().set_yticks(yticks)
    if ylabel:
      plt.ylabel(ylabel)
    plt.xlim([-40, 190])
    plt.ylim([min(yticks), max(yticks)])
    plt.plot(x, alc_data, linewidth=3)
    plt.plot(x, pla_data, linewidth=3)
    plt.rcParams["figure.figsize"] = [8, 6]
    plt.rcParams["font.weight"] = "bold"
    plt.title(f'{variable_title}', fontsize=18, fontweight = 'bold')
    plt.xlabel('Time (minutes)')
    plt.grid(False)
    plt.legend(["alcohol", "placebo"], bbox_to_anchor=(1.05, 0.95))
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.vlines([i/3 for i in list(range(0,50))], 0, (max(yticks)), color='lightgray', linestyle='solid')
    plt.annotate('ALCOHOL', (8.3, (max(alc_data)/1.9)), textcoords="offset points", xytext=(0,10), ha='center', rotation=90, fontsize=14, color='black')
    if variable_title == 'I LIKE the effect I am feeling':
        plt.hlines(50, 17, max(xticks), color='black', linestyle='dotted')
        plt.annotate('Neutral', (max(xticks)-25, 50), textcoords="offset points", xytext=(0,10), ha='center', fontsize=14, color='black')
    
    coordinates_alc = dict(zip(x, alc_data))
    coordinates_pla = dict(zip(x, pla_data))
    
    for x,y in coordinates_alc.items():
        label = y
        plt.annotate(label, (x,y), textcoords="offset points", xytext=(0,10), ha='center')

    for x,y in coordinates_pla.items():
        label = y
        plt.annotate(label, (x,y), textcoords="offset points", xytext=(0,10), ha='center')
    
    image_path = f'{path}/graphs/{subid}_{match}_AP.png'
    plt.savefig(image_path, bbox_inches='tight')
    plt.close()
    return image_path

def create_line_graph_alcohol(subid, match, variable_title, alc_data, timepoints, yticks, ylabel, path):
    variable_title
    x = timepoints
    xticks = timepoints.copy()
    xticks.insert(xticks.index(30), 0)
    if -30 not in timepoints:
        xticks.insert(xticks.index(0), -30)
    plt.gca().set_xticks(xticks)
    plt.gca().set_yticks(yticks)
    plt.xlim([-40, 190])
    plt.ylim([min(yticks), max(yticks)])
    if ylabel:
      plt.ylabel(ylabel)
    plt.plot(x, alc_data, linewidth=3)
    plt.rcParams["figure.figsize"] = [8, 6]
    plt.rcParams["font.weight"] = "bold"
    plt.title(f'{variable_title}', fontsize=18, fontweight = 'bold')
    plt.xlabel('Time (minutes)')
    plt.grid(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.vlines([i/3 for i in list(range(0,50))], 0, (max(yticks)), color='lightgray', linestyle='solid')
    plt.annotate('ALCOHOL', (8.3, (max(alc_data)/1.9)), textcoords="offset points", xytext=(0,10), ha='center', rotation=90, fontsize=14, color='black')
    if variable_title == 'I LIKE the effect I am feeling':
        plt.hlines(50, 17, max(xticks), color='black', linestyle='dotted')
        plt.annotate('Neutral', (max(xticks)-25, 50), textcoords="offset points", xytext=(0,10), ha='center', fontsize=14, color='black')
    
    coordinates_alc = dict(zip(x, alc_data))
    
    for x,y in coordinates_alc.items():
        label = y
        plt.annotate(label, (x,y), textcoords="offset points", xytext=(0,10), ha='center')
    
    image_path = f'{path}/graphs/{subid}_{match}_A.png'
    plt.savefig(image_path, bbox_inches='tight')
    plt.close()
    return image_path