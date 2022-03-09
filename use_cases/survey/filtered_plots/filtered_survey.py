import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker
from IPython.display import display
from matplotlib.ticker import MaxNLocator

# set parameters (global)
GRID = True
LOCATOR = 4
FONTSIZE = 15
FIGSIZE = (15, 15)
COLOR = "k"
PLOT_FNAME = "fig_survey_only_{}_fig{}"
PLOT_KIND = ["operators", "researchers", "CP", "DP"]
count_for_png = 0  # return it every time we call a plot function

df = pd.read_csv('SurveyAnswers.csv')

# basic cols
basic_cols = ['What is your main professional role?', 'Which term(s) would best characterize your organization?',
              'In which continent(s) does your organization operate (or is located)?',
              'What is your knowledge or experience with Internet measurements/monitoring?']

basic_cols2 = ['How many platforms do you typically use when you do measurements?',
               'How many monitors / vantage points (VPs) do you typically use in your measurements?']

# take network columns
columns_of_networks = [col for col in df.columns if 'Network types' in col]

# take importance columns
columns_of_importance = [col for col in df.columns if 'How important would be' in col]

# take trigger columns
columns_of_trigger = [col for col in df.columns if 'Which of the following types of events would trigger' in col]

# save numerical col
numerical_cols = [col for col in df.columns if 'good indication of the bias?' in col]

# measurment cols
measurement_cols = [col for col in df.columns if 'Measurement' in col]

# scope
scope_cols = [col for col in df.columns if 'Scope' in col]

# inf
inf_cols = [col for col in df.columns if 'Infrastructure / platforms' in col]

# bias
bias_cols = [col for col in df.columns if
             'Is there any kind of bias in the measurement data collected for this use case?' in col]

# bias2
bias2_cols = [col for col in df.columns if 'If yes, the bias is with respect to' in col]

# loc
loc_cols = [col for col in df.columns if 'Location' in col]


def barh_plots(df, basic_cols, count_for_png, kind):
    # set the index that divides the basic columns of the use-cases-questions columns

    # plot basic columns
    for i in range(len(basic_cols)):

        total = df[basic_cols[i]].count().sum()
        plt.figure()
        plt.grid(GRID)
        plt.rcParams.update({'font.size': FONTSIZE})

        plt.title(basic_cols[i])
        ax = df[basic_cols[i]].str.split(r',\s*(?=[^)]*(?:\(|$))', expand=True).stack().value_counts().plot(kind='barh',
                                                                                                            figsize=FIGSIZE,
                                                                                                            color='k')

        for p in ax.patches:
            percentage = '{:.1f}%'.format(100 * p.get_width() / total)
            x = p.get_x() + p.get_width() + 0.02
            y = p.get_y() + p.get_height() / 2
            ax.annotate(percentage, (x, y))

        locator = matplotlib.ticker.MultipleLocator(LOCATOR)
        ax.xaxis.set_major_locator(locator)

        plt.savefig(PLOT_FNAME.format(PLOT_KIND[kind], count_for_png), dpi=300, bbox_inches="tight")
        count_for_png += 1
    return count_for_png


def barh_plots_measurement(df, m_cols, count_for_png, kind):

    total = 0
    for i in range(len(m_cols)):
        total += df[m_cols[i]].count().sum()

    counts = []

    for col in m_cols:
        df[col] = df[col].astype(str)

    answers = ["Control", "Data", "know"]
    i = 0
    while i < len(answers):
        sum = 0
        for col in m_cols:
            sum += df[col].str.count(answers[i]).sum()

        counts.append(sum)
        i += 1

    data = []

    for i in range(len(counts)):
        data.append((answers[i], counts[i]))

    df_mes = pd.DataFrame(data, columns=['Answers', 'count'])
    df_mes.index = ["Control-plane (BGP tables and messages/updates )", "Data-plane (ping, traceroute)", "I don't know"]

    plt.figure()
    plt.rcParams.update({'font.size': FONTSIZE})

    ax = df_mes.plot(kind='barh', title=m_cols[0], figsize=FIGSIZE, color='k')

    locator = matplotlib.ticker.MultipleLocator(LOCATOR)
    ax.xaxis.set_major_locator(locator)

    for p in ax.patches:
        percentage = '{:.1f}%'.format(100 * p.get_width() / total)
        x = p.get_x() + p.get_width() + 0.02
        y = p.get_y() + p.get_height() / 2
        ax.annotate(percentage, (x, y))

    plt.savefig(PLOT_FNAME.format(PLOT_KIND[kind], count_for_png), dpi=300, bbox_inches="tight")
    count_for_png += 1
    return count_for_png


def barh_plots_scope(df, s_cols, count_for_png, kind):

    total = 0
    for i in range(len(s_cols)):
        total += df[s_cols[i]].count().sum()

    counts_d = []

    other_answers = ["update", "bgp", "AS", "PTR", "Cybersecurity"]
    default_answers = ['Paths', 'Reachability', 'Latency', 'Throughput']

    i = 0
    while i < len(default_answers):
        sum = 0
        for col in s_cols:
            sum += df[col].str.count(default_answers[i]).sum()

        counts_d.append(sum)
        i += 1

    j = 0
    other_sum_idxs = []
    while j < len(other_answers):
        idx = []
        for col in s_cols:
            idx.append(df.index[df[col].str.contains(other_answers[j], na=False)].tolist())
        other_sum_idxs.append(idx)
        j += 1


    flat_other_sum = [item for sublist in other_sum_idxs for item in sublist]
    flat_other_sum_idxs = [item for sublist in flat_other_sum for item in sublist]

    flat_other_sum_idxs = list(set(flat_other_sum_idxs))
    other_sum = len(flat_other_sum_idxs)

    data = []

    for i in range(len(counts_d)):
        data.append((default_answers[i], counts_d[i]))

    data.append(("Other", other_sum))

    df_scope = pd.DataFrame(data, columns=["Answers", "Scope_number"])
    df_scope.index = ['Paths, routing policies, topology (e.g., BGP messages, traceroutes)', 'Reachability', 'Latency',
                      'Throughput', 'Other']

    plt.figure()
    plt.rcParams.update({'font.size': FONTSIZE})

    ax = df_scope.plot(kind='barh', title=s_cols[0], figsize=FIGSIZE, color='k')

    locator = matplotlib.ticker.MultipleLocator(LOCATOR)
    ax.xaxis.set_major_locator(locator)

    for p in ax.patches:
        percentage = '{:.1f}%'.format(100 * p.get_width() / total)
        x = p.get_x() + p.get_width() + 0.02
        y = p.get_y() + p.get_height() / 2
        ax.annotate(percentage, (x, y))

    plt.savefig(PLOT_FNAME.format(PLOT_KIND[kind], count_for_png), dpi=300, bbox_inches="tight")
    count_for_png += 1
    print(
        "Other answers for Scope are: AS relationships, Uptime, bgp chum update behavior, Most often it's just a question of whether a given PTR naming is end user and what sort (dynamic residential, static business, shared or dedicated webhosting, etc.)")

    return count_for_png


def barh_plots_inf(df, inf_cols, count_for_png, kind):

    total = 0
    for ix in range(len(inf_cols)):
        total += df[inf_cols[ix]].count().sum()
    print(total)
    counts_d = []

    other_answers = ["rpki", "NLRING", "dig", "MTR.sh", "bgp.tools", "whois", "ITDK", "Speedtest.net", "isolario",
                     "PTR", "Eyes", "looking-glass", "Radar", "PeeringDB", "Euro-IX", "PHC", "scans.io"]
    default_answers = ["RIS", "Atlas", "RIPEstat", "bgp.he.net", "RouteViews", "CAIDA’s", "Ark", "M-lab", "Custom"]
    other_sum = 0

    i = 0
    while i < len(default_answers):
        summ = 0
        for col in inf_cols:

            summ += df[col].str.count(default_answers[i]).sum()

        counts_d.append(summ)
        i += 1

    j = 0
    other_sum_idxs = []
    while j < len(other_answers):
        idx = []
        for col in inf_cols:
            idx.append(df.index[df[col].str.contains(other_answers[j], na=False)].tolist())
        other_sum_idxs.append(idx)
        j += 1

    # print(other_sum_idxs)
    flat_other_sum = [item for sublist in other_sum_idxs for item in sublist]
    flat_other_sum_idxs = [item for sublist in flat_other_sum for item in sublist]

    flat_other_sum_idxs = list(set(flat_other_sum_idxs))
    other_sum = len(flat_other_sum_idxs)

    data = []

    for i in range(len(counts_d)):
        data.append((default_answers[i], counts_d[i]))

    data.append(("Other", other_sum))

    df_inf = pd.DataFrame(data, columns=["Answers", "Infrastructure"])
    df_inf.index = ["RIPE RIS", "RIPE Atlas", "RIPEstat", "bgp.he.net", "RouteViews", "CAIDA’s BGPStream", "Ark",
                    "M-lab", "Custom of proprietary measurement platform/service", "Other"]

    plt.figure()
    plt.rcParams.update({'font.size': FONTSIZE})

    ax = df_inf.plot(kind='barh', title=inf_cols[0], figsize=FIGSIZE, color='k')

    locator = matplotlib.ticker.MultipleLocator(4)
    ax.xaxis.set_major_locator(locator)

    for p in ax.patches:
        percentage = '{:.1f}%'.format(100 * p.get_width() / total)
        x = p.get_x() + p.get_width() + 0.02
        y = p.get_y() + p.get_height() / 2
        ax.annotate(percentage, (x, y))

    plt.savefig(PLOT_FNAME.format(PLOT_KIND[kind], count_for_png), dpi=300, bbox_inches="tight")
    count_for_png += 1
    print(
        "Other answers for Infrastructure / platforms / services are: rpki-clients.org and other rpki ressources, NLRING, dig, MTR.sh RIPE database, bgp.tools, whois, ITDK, Speedtest.net (ookla), isolario, We constantly run zdns PTR scans on the entirety of IPv4 via AWS, THousand Eyes, NUmerous looking-glass sites from various networks, Radar.qraot.net, PeeringDB, Euro-IX, PCH, scans.io")

    return count_for_png


def barh_plots_loc(df, loc_cols, count_for_png, kind):
    total = 0
    for i in range(len(loc_cols)):
        total += df[loc_cols[i]].count().sum()

    counts_d = []

    # just give keywords of the answers
    other_answers = ["Depend", "between", "Hyper-local", "Company", "physical"]
    default_answers = ["know", "Global-level", "Continent-level", "Country-level", "City-level"]

    i = 0
    while i < len(default_answers):
        sum = 0
        for col in loc_cols:
            sum += df[col].str.count(default_answers[i]).sum()

        counts_d.append(sum)
        i += 1

    j = 0
    other_sum = 0
    while j < len(other_answers):

        for col in loc_cols:
            other_sum += df[col].str.count(other_answers[j]).sum()

        j += 1

    data = []

    for i in range(len(counts_d)):
        data.append((default_answers[i], counts_d[i]))

    data.append(("Other", other_sum))


    df_loc = pd.DataFrame(data, columns=["Answers", "Location"])

    df_loc.index = ["I don't know", "Global-level", "Continent-level", "Country-level", "City-level", "Other"]

    df_loc.index = pd.Categorical(df_loc.index,
                                  categories=["City-level", "Country-level", "Continent-level", "Global-level",
                                              "I don't know", "Other"],
                                  ordered=True)

    plt.figure()
    plt.rcParams.update({'font.size': FONTSIZE})

    ax = df_loc.plot(kind='barh', title=loc_cols[0], figsize=FIGSIZE, color='k')

    locator = matplotlib.ticker.MultipleLocator(LOCATOR)
    ax.xaxis.set_major_locator(locator)

    for p in ax.patches:
        percentage = '{:.1f}%'.format(100 * p.get_width() / total)
        x = p.get_x() + p.get_width() + 0.02
        y = p.get_y() + p.get_height() / 2
        ax.annotate(percentage, (x, y))

    plt.savefig(PLOT_FNAME.format(PLOT_KIND[kind], count_for_png), dpi=300, bbox_inches="tight")
    count_for_png += 1
    print(
        "Other answers for location are: Local, Company, I don't care for physical locations, Global and hyper-local(eg a specific point-to-to point link) but almost nothing in between', I dont care about physical locations, Depend on situation")

    return count_for_png


def hbar_networks(df, columns_of_networks, count_for_png, kind):

    for network in columns_of_networks:
        df[network] = df[network].astype(str)

    networks = []
    tier = [col for col in columns_of_networks if 'Tier' in col]
    multin = [col for col in columns_of_networks if 'Multi-national' in col]
    reg = [col for col in columns_of_networks if 'Regional' in col]
    cont = [col for col in columns_of_networks if 'Content Distribution' in col]
    cloud = [col for col in columns_of_networks if 'Cloud provider' in col]
    mob = [col for col in columns_of_networks if 'Mobile Access' in col]
    ixp = [col for col in columns_of_networks if 'IXP' in col]
    enter = [col for col in columns_of_networks if 'Enterprise' in col]
    oth = [col for col in columns_of_networks if 'Other' in col]

    networks.append(tier)
    networks.append(multin)
    networks.append(reg)
    networks.append(cont)
    networks.append(cloud)
    networks.append(mob)
    networks.append(ixp)
    networks.append(enter)
    networks.append(oth)

    j = 0
    all_networks = []
    while j < len(networks):
        i = 0

        while i < len(networks[j]):
            sum1 = 0
            sum2 = 0
            for col in networks[j]:
                sum1 += df[col].str.count("From").sum()
                sum2 += df[col].str.count("To").sum()
            i += 1
        all_networks.append((networks[j][0], sum1, sum2))
        j += 1

    df_networks = pd.DataFrame(all_networks, columns=['Network', 'From', 'To'])
    df_networks = df_networks.set_index('Network')

    df_networks.index = df_networks.index.str.split('\[').str[-1].str.strip()
    df_networks.index = df_networks.index.str[:-1]

    plt.figure()
    plt.rcParams.update({'font.size': FONTSIZE})

    ax = df_networks.plot(kind='barh', figsize=FIGSIZE, title='Network Type')

    locator = matplotlib.ticker.MultipleLocator(10)
    ax.xaxis.set_major_locator(locator)
    ax.set(ylabel=None)
    plt.savefig(PLOT_FNAME.format(PLOT_KIND[kind], count_for_png), dpi=300, bbox_inches="tight")
    count_for_png += 1
    return count_for_png


def barh_plots_bias(df, bias_cols, count_for_png, kind):
    total = 0
    for i in range(len(bias_cols)):
        total += df[bias_cols[i]].count().sum()

    counts = []

    for col in bias_cols:
        df[col] = df[col].astype(str)

    answers = ["know", "No", "Yes"]
    i = 0
    while i < len(answers):
        sum = 0
        for col in bias_cols:
            sum += df[col].str.count(answers[i]).sum()

        counts.append(sum)
        i += 1

    data = []

    for i in range(len(counts)):
        data.append((answers[i], counts[i]))

    df_bias = pd.DataFrame(data, columns=['Answers', 'count'])
    df_bias.index = ["I don't know", "No/Probably no", "Yes/Probably yes"]

    plt.figure()
    plt.rcParams.update({'font.size': FONTSIZE})

    ax = df_bias.plot(kind='barh', title=bias_cols[0], figsize=FIGSIZE, color='k')

    locator = matplotlib.ticker.MultipleLocator(LOCATOR)
    ax.xaxis.set_major_locator(locator)

    for p in ax.patches:
        percentage = '{:.1f}%'.format(100 * p.get_width() / total)
        x = p.get_x() + p.get_width() + 0.02
        y = p.get_y() + p.get_height() / 2
        ax.annotate(percentage, (x, y))
    plt.savefig(PLOT_FNAME.format(PLOT_KIND[kind], count_for_png), dpi=300, bbox_inches="tight")
    count_for_png += 1
    return count_for_png


def barh_plots_ifyesbias(df, bias2_cols, count_for_png, kind):
    total = 0
    for i in range(len(bias2_cols)):
        total += df[bias2_cols[i]].count().sum()

    counts_d = []

    # just give keywords of the answers
    other_answers = ["partial", "imho", "nobody", "representative", "ourselves", "stub.", "Scarcity", "IPv6",
                     "filtering", "Access", "ie", "Atlas", "view"]
    default_answers = ["Geography", "types"]

    i = 0
    while i < len(default_answers):
        sum = 0
        for col in bias2_cols:
            sum += df[col].str.count(default_answers[i]).sum()

        counts_d.append(sum)
        i += 1

    j = 0
    other_sum_idxs = []
    while j < len(other_answers):
        idx = []
        for col in bias2_cols:
            idx.append(df.index[df[col].str.contains(other_answers[j], na=False)].tolist())
        other_sum_idxs.append(idx)
        j += 1

    # print(other_sum_idxs)
    flat_other_sum = [item for sublist in other_sum_idxs for item in sublist]
    flat_other_sum_idxs = [item for sublist in flat_other_sum for item in sublist]

    flat_other_sum_idxs = list(set(flat_other_sum_idxs))
    other_sum = len(flat_other_sum_idxs)

    data = []
    for i in range(len(counts_d)):
        data.append((default_answers[i], counts_d[i]))

    data.append(("Other", other_sum))

    df_bias = pd.DataFrame(data, columns=["Answers", "[Optional] If yes, the bias is with respect to...?"])

    df_bias.index = ["Geography / location (e.g., geographic locations)",
                     "Network types (e.g., eyeball, transit, CDNs)", "Other"]

    plt.figure()
    plt.rcParams.update({'font.size': FONTSIZE})

    ax = df_bias.plot(kind='barh', title=bias2_cols[0], figsize=FIGSIZE, color='k')

    locator = matplotlib.ticker.MultipleLocator(LOCATOR)
    ax.xaxis.set_major_locator(locator)

    for p in ax.patches:
        percentage = '{:.1f}%'.format(100 * p.get_width() / total)
        x = p.get_x() + p.get_width() + 0.02
        y = p.get_y() + p.get_height() / 2
        ax.annotate(percentage, (x, y))
    plt.savefig(PLOT_FNAME.format(PLOT_KIND[kind],count_for_png), dpi=300, bbox_inches="tight")
    count_for_png += 1

    print(
        "Other answers for question: If yes, the bias is with respect to...? are: Atlas is opt in you don't get a view from all networks, Acess network type ie wireless networks are generally missing, filtering from the vantage point, IPv6 HE tunnels for some RIPE Atlas probes. Would like to exclude them, Scarcity, we're stub. so covered, we often measure from ourselves, but select a representative subset depending on their needs, imho nobody should ever us all vantage points at the same time, partial coverage")

    return count_for_png


def barh_plots_num(df, numerical_cols, count_for_png, kind):
    total = 0
    for i in range(len(numerical_cols)):
        total += df[numerical_cols[i]].count().sum()

    counts = []

    for col in numerical_cols:
        df[col] = df[col].astype(str)

    answers = ["1.0", "2.0", "3.0", "4.0", "5.0"]
    i = 0
    while i < len(answers):
        sum = 0
        for col in numerical_cols:
            sum += df[col].str.count(answers[i]).sum()

        counts.append(sum)
        i += 1

    data = []

    for i in range(len(counts)):
        data.append((answers[i], counts[i]))

    df_num = pd.DataFrame(data, columns=['Answers', 'count'])
    df_num = df_num.set_index('Answers')

    plt.figure()
    plt.rcParams.update({'font.size': FONTSIZE})

    ax = df_num.plot(kind='barh', title=numerical_cols[0], figsize=FIGSIZE, color='k')

    locator = matplotlib.ticker.MultipleLocator(LOCATOR)
    ax.xaxis.set_major_locator(locator)

    for p in ax.patches:
        percentage = '{:.1f}%'.format(100 * p.get_width() / total)
        x = p.get_x() + p.get_width() + 0.02
        y = p.get_y() + p.get_height() / 2
        ax.annotate(percentage, (x, y))
    plt.savefig(PLOT_FNAME.format(PLOT_KIND[kind], count_for_png), dpi=300, bbox_inches="tight")
    count_for_png += 1
    return count_for_png


def hbar_trigger(df, columns_of_trigger, count_for_png, kind):
    triggers = []

    for trigger in columns_of_trigger:
        df[trigger] = df[trigger].astype(str)
        triggers.append((df[trigger].str.count("Would it trigger use of measurement data or infrastructure?").sum(),
                         df[trigger].str.count("Are you concerned about bias in the data?").sum()))

    data = []

    for i in range(len(triggers)):
        data.append((columns_of_trigger[i], triggers[i][0], triggers[i][1]))

    df_trigger = pd.DataFrame(data, columns=['Trigger', 'Would it trigger use of measurement data or infrastructure?',
                                             'Are you concerned about bias in the data?'])
    df_trigger = df_trigger.set_index('Trigger')

    df_trigger.index = df_trigger.index.str.split('\[').str[-1].str.strip()
    df_trigger.index = df_trigger.index.str[:-1]

    plt.figure()
    plt.rcParams.update({'font.size': FONTSIZE})

    ax = df_trigger.plot(kind='barh', figsize=FIGSIZE,
                         title='Which of the following types of events would trigger you to use measurement/monitoring data ')
    ax.set(ylabel=None)
    locator = matplotlib.ticker.MultipleLocator(LOCATOR)
    ax.xaxis.set_major_locator(locator)
    plt.savefig(PLOT_FNAME.format(PLOT_KIND[kind], count_for_png), dpi=300, bbox_inches="tight")
    count_for_png += 1
    return count_for_png


def barh_plots2(df, basic_cols2, count_for_png, kind):

    # plot basic columns
    for i in range(len(basic_cols2)):

        total = df[basic_cols2[i]].count().sum()

        plt.figure()
        plt.grid(GRID)
        plt.rcParams.update({'font.size': FONTSIZE})

        plt.title(basic_cols2[i])
        ax = df[basic_cols2[i]].str.split(r',\s*(?=[^)]*(?:\(|$))', expand=True).stack().value_counts().plot(
            kind='barh', figsize=FIGSIZE, color='k')

        for p in ax.patches:
            percentage = '{:.1f}%'.format(100 * p.get_width() / total)
            x = p.get_x() + p.get_width() + 0.02
            y = p.get_y() + p.get_height() / 2
            ax.annotate(percentage, (x, y))

        locator = matplotlib.ticker.MultipleLocator(LOCATOR)
        ax.xaxis.set_major_locator(locator)
        plt.savefig(PLOT_FNAME.format(PLOT_KIND[kind], count_for_png), dpi=300, bbox_inches="tight")
        count_for_png += 1
    return count_for_png


def hbar_importance(df, columns_of_importance, count_for_png, kind):
    importances = []

    for importance in columns_of_importance:
        df[importance] = df[importance].astype(str)
        importances.append((df[importance].str.count("1.0").sum(), df[importance].str.count("2.0").sum(),
                            df[importance].str.count("3.0").sum(), df[importance].str.count("4.0").sum(),
                            df[importance].str.count("5.0").sum()))

    data = []

    for i in range(len(importances)):
        data.append((columns_of_importance[i], importances[i][0], importances[i][1], importances[i][2],
                     importances[i][3], importances[i][4]))

    df_importance = pd.DataFrame(data, columns=['Importance', '1', '2', '3', '4', '5'])
    df_importance = df_importance.set_index('Importance')

    df_importance.index = df_importance.index.str.split('\[').str[-1].str.strip()
    df_importance.index = df_importance.index.str[:-1]

    plt.figure()
    plt.rcParams.update({'font.size': FONTSIZE})

    ax = df_importance.plot(kind='barh', figsize=FIGSIZE,
                            title='How important would be the following advances in Internet monitoring/measurements for you?')
    ax.set(ylabel=None)

    locator = matplotlib.ticker.MultipleLocator(LOCATOR)
    ax.xaxis.set_major_locator(locator)
    plt.savefig(PLOT_FNAME.format(PLOT_KIND[kind], count_for_png), dpi=300, bbox_inches="tight")
    count_for_png+=1
    return count_for_png

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# operators
df_1 = df.loc[df['What is your main professional role?'] == "Network operator / engineer"]
# researchers
df_2 = df.loc[df['What is your main professional role?'] == "Researcher"]
# display(df_2)

# measurements / control
df_c1 = df.loc[df["Measurement types"].str.contains("Control", na=False)]
df_c2 = df.loc[df["Measurement types.1"].str.contains("Control", na=False)]
df_c3 = df.loc[df["Measurement types.2"].str.contains("Control", na=False)]
idx_c = []
for i in range(0, df_c2.shape[0]):
    if df_c2.index[i] not in df_c1.index:
        idx_c.append(df_c2.index[i])

for i in range(0, df_c3.shape[0]):
    if df_c2.index[i] not in (df_c1.index and df_c2.index):
        idx_c.append(df_c3.index[i])
basic_idx_c = list(df_c1.index)
f_idx_c = basic_idx_c + idx_c
df_3 = df.iloc[f_idx_c]
# display(df_3)

# measurements / data
df_d1 = df.loc[df["Measurement types"].str.contains("Data", na=False)]
df_d2 = df.loc[df["Measurement types.1"].str.contains("Data", na=False)]
idx_d = []
# print(df_d1.index)
# print(df_d2.index)

for i in range(0, df_d2.shape[0]):
    if df_d2.index[i] not in df_d1.index:
        idx_d.append(df_d2.index[i])

basic_idx_d = list(df_d1.index)
f_idx_d = basic_idx_d + idx_d
df_4 = df.iloc[f_idx_d]
# display(df_4)

count_for_png = barh_plots(df_4, basic_cols, count_for_png, kind=3)
count_for_png = barh_plots_measurement(df_4, measurement_cols, count_for_png, kind=3)
count_for_png = barh_plots_scope(df_4, scope_cols, count_for_png, kind=3)
count_for_png = barh_plots_inf(df_4, inf_cols, count_for_png, kind=3)
count_for_png = barh_plots_loc(df_4, loc_cols, count_for_png, kind=3)
count_for_png = hbar_networks(df_4, columns_of_networks, count_for_png, kind=3)
count_for_png = barh_plots_bias(df_4, bias_cols, count_for_png, kind=3)
count_for_png = barh_plots_ifyesbias(df_4, bias2_cols, count_for_png, kind=3)
count_for_png = barh_plots_num(df_4, numerical_cols, count_for_png, kind=3)
count_for_png = hbar_trigger(df_4, columns_of_trigger, count_for_png, kind=3)
count_for_png = barh_plots2(df_4, basic_cols2, count_for_png, kind=3)
count_for_png = hbar_importance(df_4, columns_of_importance, count_for_png, kind=3)