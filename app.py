# ----------------------------------------
# FAO-based food-energy equivalent estimator
# 
# author: Krzysztof Raczynski
#
# developed: 09/14/2026
# ----------------------------------------

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
from shapely import wkt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle, Patch
import base64

st.set_page_config(
    page_title="Can You Feed a Country?",
    page_icon="🌾",
    layout="wide"
)

st.markdown(
    """
    <style>

    /* 
       PAGE LAYOUT
    */

    .block-container {
        max-width: 1450px;
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }


    /* 
       HEADINGS
    */

    h1 {
        font-size: 2.65rem !important;
        line-height: 1.12 !important;
        margin-top: 0 !important;
        margin-bottom: 0.65rem !important;
    }

    h2 {
        font-size: 1.95rem !important;
        line-height: 1.15 !important;
        margin-top: 0.8rem !important;
        margin-bottom: 0.45rem !important;
    }

    h3 {
        font-size: 1.45rem !important;
        line-height: 1.2 !important;
    }


    /* 
       NORMAL TEXT
    */

    p {
        font-size: 1.05rem !important;
        line-height: 1.45 !important;
    }

    label {
        font-size: 1.12rem !important;
        font-weight: 600 !important;
    }


    /*
       BUTTONS — TOUCH FRIENDLY
    */

    div.stButton > button {
        min-height: 3.6rem;
        font-size: 1.15rem;
        font-weight: 650;
        border-radius: 0.7rem;
        padding: 0.7rem 0.9rem;
    }


    /*
       METRICS
    */

    [data-testid="stMetric"] {
        padding-top: 0.2rem;
        padding-bottom: 0.2rem;
    }

    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
    }


    /*
       ALERT BOXES
    */

    [data-testid="stAlert"] {
        padding-top: 0.75rem;
        padding-bottom: 0.75rem;
        border-radius: 0.7rem;
    }

    [data-testid="stAlert"] p {
        font-size: 1rem !important;
    }


    /*
       RADIO BUTTONS
    */

    div[role="radiogroup"] {
        gap: 0.9rem;
    }

    div[role="radiogroup"] label {
        font-size: 1.05rem !important;
    }


    /*
       SLIDERS
    */

    [data-testid="stSlider"] {
        padding-top: 0.2rem;
        padding-bottom: 0.2rem;
    }


    /*
       METHODOLOGY FOOTER
    */

    .methodology-footer {
        font-size: 0.76rem;
        line-height: 1.4;
        opacity: 0.62;
        margin-top: 0.1rem;
        padding-bottom: 0.2rem;
    }


    /*
       TABLET / IPAD RESPONSIVE
    */

    @media (max-width: 900px) {

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 0.8rem;
        }

        h1 {
            font-size: 2.2rem !important;
        }

        h2 {
            font-size: 1.7rem !important;
        }

        div.stButton > button {
            min-height: 3.5rem;
            font-size: 1.08rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.65rem !important;
        }
    }


    /*
       REMOVE STREAMLIT CHROME
    */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
        height: 0;
    }

    [data-testid="stToolbar"] {
        display: none;
    }

    [data-testid="stDecoration"] {
        display: none;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# APP STATE

if "screen" not in st.session_state:
    st.session_state.screen = 1

if "country" not in st.session_state:
    st.session_state.country = None

if "results" not in st.session_state:
    st.session_state.results = None

if "corn" not in st.session_state:
    st.session_state.corn = 0

if "wheat" not in st.session_state:
    st.session_state.wheat = 0

if "soy" not in st.session_state:
    st.session_state.soy = 0

if "language" not in st.session_state:
    st.session_state.language = "en"

if "weather_choice" not in st.session_state:
    st.session_state.weather_choice = "drought"

COUNTRY_DATA = {
    "United States": {
        "cropland_ha": 155_000_000,
        "population": 343_500_000,
        "climate": {
            "mean_temp_c": 9.5,
            "annual_precip_mm": 760,
        },
        "yields": {
            "corn": 11.131,
            "wheat": 3.269,
            "soy": 3.399,
        },
    },

    "Italy": {
        "cropland_ha": 9_470_000,
        "population": 59_500_000,
        "climate": {
            "mean_temp_c": 13.4,
            "annual_precip_mm": 830,
        },
        "yields": {
            "corn": 10.731,
            "wheat": 3.692,
            "soy": 3.527,
        },
    },

    "India": {
        "cropland_ha": 168_000_000,
        "population": 1_438_000_000,
        "climate": {
            "mean_temp_c": 24.0,
            "annual_precip_mm": 1080,
        },
        "yields": {
            "corn": 3.545,
            "wheat": 3.521,
            "soy": 1.145,
        },
    },

    "Brazil": {
        "cropland_ha": 63_400_000,
        "population": 211_100_000,
        "climate": {
            "mean_temp_c": 25.6,
            "annual_precip_mm": 1756,
        },
        "yields": {
            "corn": 5.913,
            "wheat": 2.321,
            "soy": 3.423,
        },
    },

    "Kenya": {
        "cropland_ha": 7_450_000,
        "population": 55_339_000,
        "climate": {
            "mean_temp_c": 24.3,
            "annual_precip_mm": 669,
        },
        "yields": {
            "corn": 1.763,
            "wheat": 2.963,
            "soy": 0.893,
        },
    },

    "Australia": {
        "cropland_ha": 31_375_000,
        "population": 26_451_000,
        "climate": {
            "mean_temp_c": 21.8,
            "annual_precip_mm": 450,
        },
        "yields": {
            "corn": 4.972,
            "wheat": 3.188,
            "soy": 2.512,
        },
    },
}

with open(
    "fbs_2023.json",
    "r",
    encoding="utf-8"
) as f:

    FBS_DATA = json.load(f)

with open(
    "soy_oil_2023.json",
    "r",
    encoding="utf-8"
) as f:
    SOY_OIL_DATA = json.load(f)

countries = [
    "United States",
    "Italy",
    "India",
    "Brazil",
    "Kenya",
    "Australia"
]


WEATHER_SCENARIOS = {
    "drought": {
        "corn": 0.63,
        "wheat": 0.70,
        "soy": 0.75,
    },

    "flooding": {
        "corn": 0.61,
        "wheat": 0.79,
        "soy": 0.69,
    },

    "heat": {
        "corn": 0.78,
        "wheat": 0.82,
        "soy": 0.91,
    },

    "favorable": {
        "corn": 1.05,
        "wheat": 1.05,
        "soy": 1.05,
    },
}

WEATHER_SCENARIO_INFO = {

    "🔥 Drought": (
        "Approx. 30% seasonal crop-water deficit"
    ),

    "🌧️ Flooding": (
        "Significant flooding / waterlogging stress"
    ),

    "🥵 Extreme Heat": (
        "Approx. +3°C hot growing season"
    ),

    "🌤️ Favorable Year": (
        "Illustrative 5% yield improvement"
    ),
}

CROP_DATA = {
    "corn": {
        "label": "🌽 Corn",
    },

    "wheat": {
        "label": "🌾 Wheat",
    },

    "soy": {
        "label": "🫘 Soy",
    }
}

DAILY_CALORIES_PER_PERSON = 2500
MODEL_YEAR = 2023
annual_calories_per_person = (
    DAILY_CALORIES_PER_PERSON * 365
)


TEXT = {

    "en": {

        # General
        "app_title": "🌾 Can You Feed a Country?",
        "intro": (
            "Choose a country, design its cropland, "
            "and see how weather changes its food supply."
        ),

        # Screen 1
        "choose_country": "🌍 Choose a country",
        "population": "Population",
        "cropland": "Cropland",
        "select_country": "👆 Select a country to continue.",
        "next": "NEXT →",
        "avg_temperature": "Mean annual temperature",
        "annual_precipitation": "Mean annual precipitation",
        "climate_normal": "Climate normal: 1991–2020",

        # Screen 2
        "design_farms": "🌾 Design the farms",
        "allocate_instruction": (
            "Allocate all cropland across corn, wheat, and soy."
        ),
        "corn": "Corn",
        "wheat": "Wheat",
        "soy": "Soy",
        "cropland_allocated": "Cropland allocated",
        "cropland_remaining": "Cropland remaining",
        "allocate_remaining": "🌱 Allocate the remaining **{remaining}%**.",
        "all_allocated": "✅ All cropland allocated!",
        "weather_title": "🌦️ What happens this year?",
        "weather_instruction": "Choose the growing conditions:",
        "back": "← Back",
        "calculate": "🌾 CALCULATE FOOD SUPPLY",
        "allocate_error": "Allocate exactly 100% of the cropland first.",

        # Weather
        "drought": "🔥 Drought",
        "flooding": "🌧️ Flooding",
        "heat": "🥵 Extreme Heat",
        "favorable": "🌤️ Favorable Year",

        # Screen 3
        "result_title": "🌾 Food Security Result",
        "total_population": "Total population",
        "food_energy_equivalent": "Food-energy equivalent",
        "calorie_needs_covered": "Annual calorie needs covered",
        "normal_comparison": "Compared with a Normal Year",
        "normal_year": "🌤️ Normal year",
        "try_another": "🔄 TRY ANOTHER SCENARIO",

        # Feedback
        "very_large_gap": "This scenario leaves a very large calorie gap",
        "substantial_gap": "This scenario leaves a substantial calorie gap",
        "close_gap": "This scenario comes close, but does not meet modeled needs",
        "needs_met": "This scenario meets modeled calorie needs",
        "surplus": "This scenario produces a modeled calorie surplus",

        # Result messages
        "reduced_supply": (
            "This growing season reduced potential food-energy supply "
            "by the equivalent of **{value:.1f} million people's annual calorie needs**."
        ),
        "increased_supply": (
            "This growing season increased potential food-energy supply "
            "by the equivalent of **{value:.1f} million people's annual calorie needs**."
        ),
        "food_surplus": (
            "Food surplus: **+{value:.0f}%** above annual population calorie needs."
        ),
        "food_gap": (
            "Food-energy gap: **{value:.0f}%** of annual population needs."
        ),
        "needs_fully_met": (
            "🌟 Population food-energy needs are fully met, "
            "with a modeled surplus of **+{value:.0f}%**."
        ),

        # Footer
        "footer": (
            "<b>Educational model.</b> Base data use 2023 FAOSTAT / UN statistics "
            "for population, cropland, crop yields, commodity utilization, and "
            "soybean-oil use. Weather effects are literature-informed scenarios. "
            "Results represent potential annual food-energy equivalents using a "
            "2,500 kcal/person/day benchmark; actual food security also depends on "
            "diet quality, trade, access, affordability, distribution, losses, and other factors."
            "<b>Developed</b> by Krzysztof Raczynski, GEO Project, Mississippi State University, USA"
        ),
    },


    "it": {

        # General
        "app_title": "🌾 Riesci a nutrire un Paese?",
        "intro": (
            "Scegli un Paese, distribuisci i terreni coltivabili "
            "e scopri come le condizioni meteorologiche influenzano "
            "la disponibilità alimentare."
        ),

        # Screen 1
        "choose_country": "🌍 Scegli un Paese",
        "population": "Popolazione",
        "cropland": "Terreni coltivabili",
        "select_country": "👆 Seleziona un Paese per continuare.",
        "next": "AVANTI →",
        "avg_temperature": "Temperatura media annuale",
        "annual_precipitation": "Precipitazione media annuale",
        "climate_normal": "Media climatica: 1991–2020",

        # Screen 2
        "design_farms": "🌾 Organizza le coltivazioni",
        "allocate_instruction": (
            "Distribuisci tutti i terreni coltivabili tra mais, grano e soia."
        ),
        "corn": "Mais",
        "wheat": "Grano",
        "soy": "Soia",
        "cropland_allocated": "Terreni assegnati",
        "cropland_remaining": "Terreni rimanenti",
        "allocate_remaining": "🌱 Assegna il restante **{remaining}%**.",
        "all_allocated": "✅ Tutti i terreni sono stati assegnati!",
        "weather_title": "🌦️ Cosa succede quest'anno?",
        "weather_instruction": "Scegli le condizioni di crescita:",
        "back": "← Indietro",
        "calculate": "🌾 CALCOLA LA DISPONIBILITÀ ALIMENTARE",
        "allocate_error": "Assegna esattamente il 100% dei terreni coltivabili.",

        # Weather
        "drought": "🔥 Siccità",
        "flooding": "🌧️ Alluvione",
        "heat": "🥵 Caldo estremo",
        "favorable": "🌤️ Annata favorevole",

        # Screen 3
        "result_title": "🌾 Risultato sulla sicurezza alimentare",
        "total_population": "Popolazione totale",
        "food_energy_equivalent": "Equivalente energetico alimentare",
        "calorie_needs_covered": "Fabbisogno calorico annuale coperto",
        "normal_comparison": "Confronto con un'annata normale",
        "normal_year": "🌤️ Annata normale",
        "try_another": "🔄 PROVA UN ALTRO SCENARIO",

        # Feedback
        "very_large_gap": "Questo scenario lascia un deficit calorico molto elevato",
        "substantial_gap": "Questo scenario lascia un deficit calorico significativo",
        "close_gap": "Questo scenario si avvicina, ma non soddisfa il fabbisogno stimato",
        "needs_met": "Questo scenario soddisfa il fabbisogno calorico stimato",
        "surplus": "Questo scenario produce un surplus calorico stimato",

        # Result messages
        "reduced_supply": (
            "Questa stagione di crescita ha ridotto la disponibilità potenziale "
            "di energia alimentare dell'equivalente del fabbisogno calorico annuale "
            "di **{value:.1f} milioni di persone**."
        ),
        "increased_supply": (
            "Questa stagione di crescita ha aumentato la disponibilità potenziale "
            "di energia alimentare dell'equivalente del fabbisogno calorico annuale "
            "di **{value:.1f} milioni di persone**."
        ),
        "food_surplus": (
            "Surplus alimentare: **+{value:.0f}%** rispetto al fabbisogno calorico "
            "annuale della popolazione."
        ),
        "food_gap": (
            "Deficit energetico alimentare: **{value:.0f}%** del fabbisogno annuale "
            "della popolazione."
        ),
        "needs_fully_met": (
            "🌟 Il fabbisogno energetico alimentare della popolazione è pienamente "
            "soddisfatto, con un surplus stimato di **+{value:.0f}%**."
        ),

        # Footer
        "footer": (
            "<b>Modello educativo.</b> I dati di base utilizzano statistiche "
            "FAOSTAT / ONU del 2023 relative a popolazione, terreni coltivabili, "
            "rese agricole, utilizzo delle materie prime e uso dell'olio di soia. "
            "Gli effetti meteorologici rappresentano scenari basati sulla letteratura "
            "scientifica. I risultati rappresentano equivalenti potenziali "
            "di energia alimentare annuale utilizzando un valore di "
            "riferimento di 2.500 kcal/persona/giorno; "
            "la sicurezza alimentare reale dipende anche dalla qualità della dieta, "
            "dal commercio, dall'accesso, dall'accessibilità economica, dalla "
            "distribuzione, dalle perdite alimentari e da altri fattori."
            "<b>Sviluppato</b> da Krzysztof Raczynski, GEO Project, Mississippi State University, USA"
        ),
    },
}

COUNTRY_LABELS = {

    "en": {
        "United States": "United States",
        "Italy": "Italy",
        "India": "India",
        "Brazil": "Brazil",
        "Kenya": "Kenya",
        "Australia": "Australia",
    },

    "it": {
        "United States": "Stati Uniti",
        "Italy": "Italia",
        "India": "India",
        "Brazil": "Brasile",
        "Kenya": "Kenya",
        "Australia": "Australia",
    },
}

WEATHER_KEYS = [
    "drought",
    "flooding",
    "heat",
    "favorable"
]

def set_language(language):
    st.session_state.language = language


def weather_label(weather_key):

    labels = {
        "drought": t("drought"),
        "flooding": t("flooding"),
        "heat": t("heat"),
        "favorable": t("favorable"),
    }

    return labels[weather_key]

def t(key):
    return TEXT[st.session_state.language][key]

def country_label(country):
    return COUNTRY_LABELS[
        st.session_state.language
    ][country]

def image_to_data_uri(path):

    with open(path, "rb") as f:
        encoded = base64.b64encode(
            f.read()
        ).decode()

    return f"data:image/png;base64,{encoded}"

def calculate_crop_calories(
    country,
    crop,
    cropland_ha,
    allocation_percent,
    yield_t_ha,
    weather_factor
):
    area_ha = (
        cropland_ha
        * allocation_percent
        / 100
    )

    production_t = (
        area_ha
        * yield_t_ha
        * weather_factor
    )

    production_kg = (
        production_t
        * 1000
    )

    fbs = FBS_DATA[country][crop]

    food_share = fbs["food_share"]
    food_kcal_per_kg = fbs["food_kcal_per_kg"]

    if crop in ["corn", "wheat"]:

        usable_calories = (
            production_kg
            * food_share
            * food_kcal_per_kg
        )

    elif crop == "soy":

        domestic_supply = (
            fbs["domestic_supply_1000_t"]
        )

        processing = (
            fbs["processing_1000_t"]
        )

        if (
            domestic_supply is not None
            and domestic_supply > 0
            and processing is not None
        ):
            processing_share = (
                processing
                / domestic_supply
            )
        else:
            processing_share = 0.0

        direct_food_calories = 0.0

        if (
            food_share is not None
            and food_kcal_per_kg is not None
        ):
            direct_food_calories = (
                production_kg
                * food_share
                * food_kcal_per_kg
            )

        soy_oil_food_share = (
            SOY_OIL_DATA[country]["food_share"]
        )

        if soy_oil_food_share is None:
            soy_oil_food_share = 0.0

        SOY_OIL_YIELD = 0.18
        SOY_OIL_KCAL_PER_KG = 8840

        soybean_oil_calories = (
            production_kg
            * processing_share
            * SOY_OIL_YIELD
            * soy_oil_food_share
            * SOY_OIL_KCAL_PER_KG
        )

        usable_calories = (
            direct_food_calories
            + soybean_oil_calories
        )

    return usable_calories


def calculate_scenario(
    country,
    country_info,
    allocations,
    weather_factors
):
    total_calories = 0

    for crop, allocation in allocations.items():

        crop_calories = calculate_crop_calories(
            country=country,
            crop=crop,
            cropland_ha=country_info["cropland_ha"],
            allocation_percent=allocation,
            yield_t_ha=country_info["yields"][crop],
            weather_factor=weather_factors[crop]
        )

        total_calories += crop_calories

    people_fed = (
        total_calories
        / annual_calories_per_person
    )

    return people_fed

@st.cache_data
def load_country_shapes(path="shape.xlsx"):
    df = pd.read_excel(path)

    shapes = {}

    for _, row in df.iterrows():
        name = row["shapeName"]
        geom = wkt.loads(row["wkt_geom"])
        shapes[name] = geom

    return shapes

COUNTRY_SHAPES = load_country_shapes("shape.xlsx")

def polygon_to_path(poly):
    vertices = []
    codes = []

    exterior = list(poly.exterior.coords)
    vertices.extend(exterior)
    codes.extend(
        [Path.MOVETO]
        + [Path.LINETO] * (len(exterior) - 2)
        + [Path.CLOSEPOLY]
    )

    for interior in poly.interiors:
        ring = list(interior.coords)
        vertices.extend(ring)
        codes.extend(
            [Path.MOVETO]
            + [Path.LINETO] * (len(ring) - 2)
            + [Path.CLOSEPOLY]
        )

    return Path(vertices, codes)

def render_language_switch():

    spacer, en_col, it_col = st.columns(
        [6, 1.2, 1.2]
    )

    us_flag = image_to_data_uri(
        "assets/us.png"
    )

    italy_flag = image_to_data_uri(
        "assets/it.png"
    )

    with en_col:

        en_type = (
            "primary"
            if st.session_state.language == "en"
            else "secondary"
        )

        st.button(
            f"![US]({us_flag}) English",
            type=en_type,
            use_container_width=True,
            key="language_en",
            on_click=set_language,
            args=("en",)
        )

    with it_col:

        it_type = (
            "primary"
            if st.session_state.language == "it"
            else "secondary"
        )

        st.button(
            f"![IT]({italy_flag}) Italiano",
            type=it_type,
            use_container_width=True,
            key="language_it",
            on_click=set_language,
            args=("it",)
        )
        
def geometry_to_patch(geom, **kwargs):
    if geom.geom_type == "Polygon":
        compound_path = polygon_to_path(geom)

    elif geom.geom_type == "MultiPolygon":
        paths = [polygon_to_path(poly) for poly in geom.geoms]
        compound_path = Path.make_compound_path(*paths)

    else:
        raise ValueError(f"Unsupported geometry type: {geom.geom_type}")

    return PathPatch(compound_path, **kwargs)

CROP_COLORS = {
    "corn": "#f4c542",
    "wheat": "#d8c27a",
    "soy": "#5aa469",
}

def get_plot_theme_colors():
    theme = st.get_option("theme.base")

    if theme == "dark":
        return {
            "outline": "#F3F4F6",
            "text": "#F3F4F6",
            "empty": "#374151",
        }

    return {
        "outline": "#374151",
        "text": "#374151",
        "empty": "#D1D5DB",
    }

def render_progress():

    labels = {
        1: "● ○ ○",
        2: "● ● ○",
        3: "● ● ●",
    }

    st.markdown(
        f"<div style='text-align:center; opacity:0.45; "
        f"font-size:0.85rem; margin-bottom:0.2rem;'>"
        f"{labels[st.session_state.screen]}"
        f"</div>",
        unsafe_allow_html=True
    )

def plot_crop_mix_in_country(geom, allocations):
    colors = get_plot_theme_colors()
    fig, ax = plt.subplots(figsize=(4.5, 4.5))

    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    minx, miny, maxx, maxy = geom.bounds

    width = maxx - minx
    height = maxy - miny

    pad_x = width * 0.08
    pad_y = height * 0.08

    ax.set_xlim(
        minx - pad_x,
        maxx + pad_x
    )

    ax.set_ylim(
        miny - pad_y,
        maxy + pad_y
    )

    ax.set_aspect("equal")
    ax.axis("off")

    base = geometry_to_patch(
        geom,
        facecolor=colors["empty"],
        edgecolor=colors["outline"],
        linewidth=2.5,
        alpha=0.75
    )

    ax.add_patch(base)

    clip_patch = geometry_to_patch(
        geom,
        facecolor="none",
        edgecolor="none"
    )

    ax.add_patch(clip_patch)

    current_bottom = miny

    for crop in ["corn", "wheat", "soy"]:

        fraction = allocations[crop] / 100

        fill_height = height * fraction

        if fill_height > 0:

            rect = Rectangle(
                (minx, current_bottom),
                width,
                fill_height,
                facecolor=CROP_COLORS[crop],
                edgecolor="none",
                alpha=0.95
            )

            rect.set_clip_path(clip_patch)

            ax.add_patch(rect)

            current_bottom += fill_height

    outline = geometry_to_patch(
        geom,
        facecolor="none",
        edgecolor=colors["outline"],
        linewidth=2.5
    )

    ax.add_patch(outline)

    return fig

def plot_food_fill_in_country(geom, population_fraction):
    colors = get_plot_theme_colors()
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    fig.patch.set_alpha(0)

    minx, miny, maxx, maxy = geom.bounds
    width = maxx - minx
    height = maxy - miny

    pad_x = width * 0.05
    pad_y = height * 0.05

    ax.set_xlim(minx - pad_x, maxx + pad_x)
    ax.set_ylim(miny - pad_y, maxy + pad_y)
    ax.set_aspect("equal")
    ax.axis("off")

    background = geometry_to_patch(
        geom,
        facecolor=colors["empty"],
        edgecolor=colors["outline"],
        linewidth=2,
        alpha=0.75
    )
    ax.add_patch(background)

    clip_patch = geometry_to_patch(
        geom,
        facecolor="none",
        edgecolor="none"
    )
    ax.add_patch(clip_patch)

    fill_fraction = max(0, min(population_fraction, 1.0))
    fill_height = height * fill_fraction

    if fill_height > 0:
        rect = Rectangle(
            (minx, miny),
            width,
            fill_height,
            facecolor="#22c55e",
            edgecolor="none",
            alpha=0.95
        )
        rect.set_clip_path(clip_patch)
        ax.add_patch(rect)

    outline = geometry_to_patch(
        geom,
        facecolor="none",
        edgecolor=colors["outline"],
        linewidth=2.2
    )
    ax.add_patch(outline)

    if population_fraction > 1:
        surplus_percent = (population_fraction - 1) * 100
        ax.text(
            0.5,
            1.04,
            f"Surplus: +{surplus_percent:.0f}%",
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
            color=colors["text"]
        )

    return fig


def limit_crop_allocation(changed_crop):
    crop_keys = ["corn", "wheat", "soy"]

    other_total = sum(
        st.session_state[crop]
        for crop in crop_keys
        if crop != changed_crop
    )

    maximum_allowed = 100 - other_total

    if st.session_state[changed_crop] > maximum_allowed:
        st.session_state[changed_crop] = maximum_allowed

def get_food_security_feedback(population_fraction):

    percent = population_fraction * 100

    if percent < 40:
        return "😟", t("very_large_gap")

    elif percent < 70:
        return "😕", t("substantial_gap")

    elif percent < 100:
        return "🙂", t("close_gap")

    elif percent <= 120:
        return "🎉", t("needs_met")

    else:
        return "🌟", t("surplus")

def render_methodology_footer():

    st.markdown("---")

    st.markdown(
        f"""
        <div class="methodology-footer">
        {t("footer")}
        </div>
        """,
        unsafe_allow_html=True
    )

# SCREEN 1

if st.session_state.screen == 1:

    render_language_switch()
    render_progress()
    st.title(t("app_title"))

    st.write(t("intro"))

    st.header(t("choose_country"))

    def country_button(image_path, name):

        is_selected = (
            st.session_state.country == name
        )

        display_name = country_label(name)

        flag_uri = image_to_data_uri(image_path)

        if is_selected:
            label = (
                f"![flag]({flag_uri}) "
                f"✓ {display_name}"
            )
            button_type = "primary"

        else:
            label = (
                f"![flag]({flag_uri}) "
                f"{display_name}"
            )
            button_type = "secondary"

        if st.button(
            label,
            key=f"country_{name}",
            use_container_width=True,
            type=button_type
        ):
            st.session_state.country = name
            st.rerun()

    row1 = st.columns(3, gap="medium")

    with row1[0]:
        country_button(
            "assets/us.png",
            "United States"
        )

    with row1[1]:
        country_button(
            "assets/it.png",
            "Italy"
        )

    with row1[2]:
        country_button(
            "assets/in.png",
            "India"
        )

    row2 = st.columns(3, gap="medium")

    with row2[0]:
        country_button(
            "assets/br.png",
            "Brazil"
        )

    with row2[1]:
        country_button(
            "assets/ke.png",
            "Kenya"
        )

    with row2[2]:
        country_button(
            "assets/au.png",
            "Australia"
        )

    selected_country = st.session_state.country

    if selected_country:

        info = COUNTRY_DATA[selected_country]

        st.markdown(f"### {country_label(selected_country)}")

        stat1, stat2, stat3, stat4 = st.columns(4)

        with stat1:

            population = info["population"]

            if population >= 1_000_000_000:

                if st.session_state.language == "it":
                    population_text = (
                        f"{population / 1_000_000_000:.2f} miliardi"
                    )
                else:
                    population_text = (
                        f"{population / 1_000_000_000:.2f} billion"
                    )

            else:

                if st.session_state.language == "it":
                    population_text = (
                        f"{population / 1_000_000:.1f} milioni"
                    )
                else:
                    population_text = (
                        f"{population / 1_000_000:.1f} million"
                    )

            st.metric(t("population"), population_text)

        with stat2:

            cropland_value = (info["cropland_ha"]/ 1_000_000)

            if st.session_state.language == "it":

                cropland_text = (f"{cropland_value:.1f} milioni ha")

            else:

                cropland_text = (f"{cropland_value:.1f} million ha")

            st.metric(t("cropland"), cropland_text)

        with stat3:
            st.metric(
                t("avg_temperature"),
                f"{info['climate']['mean_temp_c']:.1f} °C"
            )

        with stat4:
            st.metric(
                t("annual_precipitation"),
                f"{info['climate']['annual_precip_mm']:,.0f} mm"
            )

    else:

        st.info(t("select_country"))


    if st.button(
        t("next"),
        type="primary",
        use_container_width=True,
        disabled=(selected_country is None)
    ):

        st.session_state.corn = 0
        st.session_state.wheat = 0
        st.session_state.soy = 0

        st.session_state.weather_choice = "drought"

        st.session_state.screen = 2

        st.rerun()

    render_methodology_footer()

# SCREEN 2

elif st.session_state.screen == 2:
    render_language_switch()
    render_progress()
    country = st.session_state.country
    country_info = COUNTRY_DATA[country]
    country_geom = COUNTRY_SHAPES[country]

    st.title(f"{t('design_farms')} — {country_label(country)}")

    left_col, right_col = st.columns([1.55, 0.85], gap="large")

    with left_col:
        st.caption(t("allocate_instruction"))

        st.slider(
            f"🌽 {t('corn')}",
            min_value=0,
            max_value=100,
            step=5,
            key="corn",
            on_change=limit_crop_allocation,
            args=("corn",)
        )

        st.slider(
            f"🌾 {t('wheat')}",
            min_value=0,
            max_value=100,
            step=5,
            key="wheat",
            on_change=limit_crop_allocation,
            args=("wheat",)
        )

        st.slider(
            f"🫘 {t('soy')}",
            min_value=0,
            max_value=100,
            step=5,
            key="soy",
            on_change=limit_crop_allocation,
            args=("soy",)
        )

        crop_total = (
            st.session_state.corn
            + st.session_state.wheat
            + st.session_state.soy
        )

        remaining = 100 - crop_total

        col_used, col_remaining = st.columns(2)

        with col_used:
            st.metric(
                t("cropland_allocated"),
                f"{crop_total}%"
            )

        with col_remaining:
            st.metric(
                t("cropland_remaining"),
                f"{remaining}%"
            )


        if crop_total < 100:

            st.warning(t("allocate_remaining").format(remaining=remaining))

        else:

            st.success(t("all_allocated"))

        st.header(t("weather_title"))

        weather = st.radio(
            t("weather_instruction"),
            WEATHER_KEYS,
            horizontal=True,
            key="weather_choice",
            format_func=weather_label
        )

        col_back, col_calc = st.columns(2)

        with col_back:
            if st.button(t("back"), use_container_width=True):
                st.session_state.screen = 1
                st.rerun()

        with col_calc:
            if st.button(
                t("calculate"),
                type="primary",
                use_container_width=True
            ):
                if crop_total != 100:
                    st.error(t("allocate_error"))
                else:
                    allocations = {
                        "corn": st.session_state.corn,
                        "wheat": st.session_state.wheat,
                        "soy": st.session_state.soy
                    }

                    scenario_people = calculate_scenario(
                        country,
                        country_info,
                        allocations,
                        WEATHER_SCENARIOS[weather]
                    )

                    normal_weather = {
                        "corn": 1.0,
                        "wheat": 1.0,
                        "soy": 1.0
                    }

                    normal_people = calculate_scenario(
                        country,
                        country_info,
                        allocations,
                        normal_weather
                    )

                    st.session_state.results = {
                        "country": country,
                        "weather": weather,
                        "corn": st.session_state.corn,
                        "wheat": st.session_state.wheat,
                        "soy": st.session_state.soy,
                        "people_fed": scenario_people,
                        "normal_people": normal_people
                    }

                    st.session_state.screen = 3
                    st.rerun()

    with right_col:
        allocations = {
            "corn": st.session_state.corn,
            "wheat": st.session_state.wheat,
            "soy": st.session_state.soy
        }

        fig = plot_crop_mix_in_country(country_geom, allocations)
        st.pyplot(fig, use_container_width=False)
        plt.close(fig)

        leg1, leg2, leg3 = st.columns(3)

        with leg1:
            st.markdown(
                f"🟨 **{t('corn')}**  \n{allocations['corn']}%"
            )

        with leg2:
            st.markdown(
                f"🟫 **{t('wheat')}**  \n{allocations['wheat']}%"
            )

        with leg3:
            st.markdown(
                f"🟩 **{t('soy')}**  \n{allocations['soy']}%"
            )

    render_methodology_footer()


# SCREEN 3 — RESULTS

elif st.session_state.screen == 3:
    render_language_switch()
    render_progress()
    results = st.session_state.results

    country = results["country"]
    country_info = COUNTRY_DATA[country]
    country_geom = COUNTRY_SHAPES[country]

    people_fed = results["people_fed"]
    normal_people = results["normal_people"]

    population_fraction = (
        people_fed
        / country_info["population"]
    )

    percent_population = population_fraction * 100
    needs_met_percent = min(percent_population, 100)
    surplus_percent = max(percent_population - 100, 0)
    people_difference = people_fed - normal_people

    

    feedback_icon, feedback_text = get_food_security_feedback(population_fraction)

    st.title(t("result_title"))
    st.caption(f"{weather_label(results['weather'])} · {country_label(country)}")

    left_col, right_col = st.columns([1.55, 0.8])

    with left_col:
        metric1, metric2, metric3 = st.columns(3)

        with metric1:
            population = country_info["population"]

            if population >= 1_000_000_000:
                population_label = f"{population / 1_000_000_000:.2f} B"
            else:
                population_label = f"{population / 1_000_000:.1f} M"

            st.metric(t("total_population"), population_label)

        with metric2:
            st.metric(t("food_energy_equivalent"), f"{people_fed / 1_000_000:.1f} M")

        with metric3:
            st.metric(  t("calorie_needs_covered"),  f"{percent_population:.0f}%")

        st.markdown(f"### {feedback_icon} {feedback_text}")

        st.subheader(t("normal_comparison"))

        col1, col2 = st.columns(2)

        with col1:
            st.metric(    t("normal_year"),    f"{normal_people / 1_000_000:.1f} M")

        with col2:
            difference_percent = (
                people_difference
                / normal_people
                * 100
            )

            st.metric(
                weather_label(results["weather"]),
                f"{people_fed / 1_000_000:.1f} M",
                delta=f"{difference_percent:.0f}%"
            )

        if people_difference < 0:

            st.warning(t("reduced_supply").format(value=( abs(people_difference)/ 1_000_000)))

        elif people_difference > 0:

            st.success(t("increased_supply").format(value=(people_difference/ 1_000_000)))

        if population_fraction > 1:

            st.info(t("food_surplus").format(value=(population_fraction - 1) * 100))

        if st.button(t("try_another"),use_container_width=True):
            st.session_state.screen = 1
            st.session_state.country = None
            st.session_state.results = None
            st.session_state.corn = 0
            st.session_state.wheat = 0
            st.session_state.soy = 0
            st.session_state.weather_choice = "drought"
            st.rerun()

    with right_col:
        if population_fraction < 1:

            gap_percent = (
                100
                - percent_population
            )

            st.info(
                t("food_gap").format(
                    value=gap_percent
                )
            )

        else:

            surplus_percent = (
                population_fraction - 1
            ) * 100

            st.success(
                t("needs_fully_met").format(
                    value=surplus_percent
                )
            )
        fig = plot_food_fill_in_country(country_geom, population_fraction)
        st.pyplot(fig, use_container_width=False)
        plt.close(fig)

    render_methodology_footer()
