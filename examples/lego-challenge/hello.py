import pandas as pd
import plotly.express as px
from numpy.random import randint
from plotly.graph_objects import Figure

from preswald import (
    Workflow,
    alert,
    button,
    connect,
    get_df,
    image,
    plotly,
    selectbox,
    separator,
    table,
    text,
    topbar,
)


# ------ Define helper functions ------


def get_area_of_foot(shoe_size: int) -> float:
    """Uses EU shoe size to estimate the area of the foot in cm^2
    Args:
        shoe_size: EU shoe size

    Returns:
        area_of_foot: area of the foot in cm^2

    References:
        [foot length](https://en.wikipedia.org/wiki/Shoe_size)
        [foot width](https://oaji.net/articles/2015/1264-1431011777.pdf)
    """

    foot_length = (2 / 3) * (shoe_size - 2)
    foot_width = 0.35 * foot_length

    # Assuming the foot is a rectangle
    return foot_length * foot_width


def get_num_legos_stepped_on(shoe_size: int) -> int:
    """Uses the area of the foot to estimate the number of legos stepped on
    Args:
        shoe_size: EU shoe size

    Returns:
        num_legos_stepped_on: number of legos stepped on
    """
    area_of_foot = get_area_of_foot(shoe_size)
    # Assuming each lego has an area of 2.34 x 2.34 cm (3x3 studs)
    area_of_lego_block = 2.34 * 2.34

    num_legos_per_foot = area_of_foot / area_of_lego_block
    num_legos_stepped_on = num_legos_per_foot * 2

    # Round to an integer and add some randomness (maybe you'll get lucky.... or not!)
    return int(num_legos_stepped_on) + randint(-10, 10)


def get_lego_color_map(legos_stepped_on: pd.DataFrame) -> dict:
    """Get the color mappings for the legos stepped on
    Args:
        legos_stepped_on: subset of the lego pile

    Returns:
        color_mappings: dictionary of color mappings
    """
    colors = legos_stepped_on[["color_name", "rgb"]].drop_duplicates()
    color_mappings = {}
    for __, row in colors.iterrows():
        color_mappings[row["color_name"]] = "#" + row["rgb"]
    return color_mappings


def visualize_lego_colors(legos_stepped_on: pd.DataFrame) -> Figure:
    """Visualizes the colors of the legos stepped on using a treemap

    Args:
        legos_stepped_on: subset of the lego pile

    Returns:
        fig: plotly figure of the treemap
    """
    color_map = get_lego_color_map(legos_stepped_on)
    fig = px.treemap(
        legos_stepped_on.color_name.value_counts().reset_index(drop=False),
        path=["color_name"],
        values="count",
        color="color_name",
        color_discrete_map=color_map,
        title="Legos Stepped on by Color",
    )
    fig.update_traces(
        textposition="top center",
        hovertemplate="<b>Color</b>: %{label} \n" + "<b>Count</b>: %{value}",
    )
    fig.update_layout(template="plotly_white")
    return fig


def get_death_roll(legos_stepped_on: pd.DataFrame) -> pd.DataFrame:
    """Get a table of the minifigs/minidolls stepped on
    Args:
        legos_stepped_on: subset of the lego pile
    Returns:
        death_roll: Minifigs/Minidolls (and heads) stepped on
    """

    death_roll = legos_stepped_on[
        [
            name in ("Minifigs", "Minifig Heads", "Minidoll Heads")
            for name in legos_stepped_on.part_cat_name
        ]
    ][["part_name", "img_url"]]
    return death_roll


def calculate_damage(legos_stepped_on: pd.DataFrame) -> int:
    """Calculate the damage taken from the legos stepped on

    Each lego piece is worth 1 point of damage, except Duplo which is 2 points.

    Args:
        legos_stepped_on: subset of the lego pile

    Returns:
        damage: damage taken
    """
    base_damage = len(legos_stepped_on)
    duplo_damage = legos_stepped_on.part_cat_name.str.contains("Duplo").sum()
    return base_damage + duplo_damage


# ------ Define app workflow ------

# Create a workflow instance
workflow = Workflow()


@workflow.atom()
def render_topbar():
    topbar()


@workflow.atom()
def render_header():
    text("# Welcome to the Lego Challenge! 🧱")


@workflow.atom()
def dump_out_legos():
    connect()
    lego_pile = get_df("lego_pile")
    text(
        "You walk into the challenge room and every inch of the floor is **covered** in Legos."
    )
    text(f"## There are {len(lego_pile)} Legos! 😱😨")
    table(lego_pile.head(100))
    separator()
    return lego_pile


@workflow.atom()
def challenge_user():
    text("# Are you brave enough to take a step?")


@workflow.atom()
def choose_shoe_size() -> int:
    text("Please select your shoe size (EU)")
    shoe_size = selectbox(
        "shoe_size",
        options=list(range(30, 50)),
        default=None,
    )
    text(f"You have selected size {shoe_size}.")
    return shoe_size


@workflow.atom(dependencies=["choose_shoe_size"])
def take_a_step() -> bool:
    step = button("Take a step", can_be_reclicked=True)
    separator()
    return step


@workflow.atom(dependencies=["take_a_step", "choose_shoe_size", "dump_out_legos"])
def get_legos_stepped_on(take_a_step, choose_shoe_size, dump_out_legos):
    if take_a_step:
        # Sample the legos stepped on
        num_legos_stepped_on = get_num_legos_stepped_on(choose_shoe_size)
        legos_stepped_on = dump_out_legos.sample(num_legos_stepped_on)

        # Get one random minifig head
        token_minifig = dump_out_legos[
            (dump_out_legos.part_cat_name == "Minifig Heads")
            & (dump_out_legos.img_url.notna())
        ].sample(1)

        # Add a random minifig to legos_stepped_on (in case no minifigs are stepped on)
        legos_stepped_on = pd.concat([legos_stepped_on, token_minifig])
        num_legos_stepped_on += 1

        text(f"# 💥💥You stepped on {num_legos_stepped_on} legos!💥💥", size=50)
        return legos_stepped_on


@workflow.atom(dependencies=["get_legos_stepped_on"])
def render_legos_stepped_on(get_legos_stepped_on):
    colors_fig = visualize_lego_colors(get_legos_stepped_on)
    plotly(colors_fig)


@workflow.atom(dependencies=["get_legos_stepped_on"])
def render_death_roll(get_legos_stepped_on):
    # Show Minifigs vanquished with step
    minifigs_vanquished = get_death_roll(get_legos_stepped_on)
    text(
        f"## **You vanquished {len(minifigs_vanquished)} Minifig{'s' if len(minifigs_vanquished) > 1 else ''} 💀⚔️**"
    )
    text("_(victorious trumpet sounds)_")

    if len(minifigs_vanquished.dropna()) > 0:
        # Get the first minifig in the death roll that has an image
        featured_enemy = minifigs_vanquished.dropna().iloc[0]
        text("### 🏆 Featured Enemy:")
        text(featured_enemy["part_name"])
        image(
            featured_enemy["img_url"],
            alt=featured_enemy["part_name"],
            size=0.7,
        )


@workflow.atom(dependencies=["get_legos_stepped_on"])
def render_damage(get_legos_stepped_on):
    damage = calculate_damage(get_legos_stepped_on)
    text(f"## Total Damage Taken: {damage}")
    alert("Damage calculation is 1 point per Lego, 2 points per Duplo.")


# Execute the workflow
results = workflow.execute()
