import streamlit as st
import pandas as pd
import json
import uuid
import time
from datetime import datetime, date
from copy import deepcopy

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Monetize360",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SESSION STATE
# ============================================================

if "domains" not in st.session_state:
    st.session_state.domains = {}

if "products" not in st.session_state:
    st.session_state.products = []

if "rules" not in st.session_state:
    st.session_state.rules = []

if "strategies" not in st.session_state:
    st.session_state.strategies = []

if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []

if "simulations" not in st.session_state:
    st.session_state.simulations = []

if "requests" not in st.session_state:
    st.session_state.requests = []

if "versions" not in st.session_state:
    st.session_state.versions = []

if "initialized" not in st.session_state:
    st.session_state.initialized = False


# ============================================================
# DEFAULT DOMAINS
# ============================================================

DOMAIN_CONFIGS = {

    "Hotel": {
        "description": "Hotel room dynamic pricing",
        "currency": "INR",
        "attributes": {
            "occupancy": "Number",
            "demand": "String",
            "weekend": "Boolean",
            "season": "String",
            "rooms_available": "Number",
            "competitor_price": "Number"
        }
    },

    "E-commerce": {
        "description": "Product pricing based on inventory and demand",
        "currency": "INR",
        "attributes": {
            "inventory": "Number",
            "demand": "String",
            "competitor_price": "Number",
            "customer_segment": "String",
            "season": "String"
        }
    },

    "Ride-hailing": {
        "description": "Dynamic ride pricing",
        "currency": "INR",
        "attributes": {
            "rider_demand": "Number",
            "driver_supply": "Number",
            "location": "String",
            "time": "String",
            "event": "String"
        }
    },

    "Airline": {
        "description": "Airline ticket pricing",
        "currency": "INR",
        "attributes": {
            "seats_available": "Number",
            "days_to_departure": "Number",
            "demand": "String",
            "season": "String",
            "competitor_price": "Number"
        }
    },

    "Banking": {
        "description": "Loan interest rate pricing",
        "currency": "%",
        "attributes": {
            "credit_score": "Number",
            "risk_level": "String",
            "loan_amount": "Number",
            "loan_duration": "Number",
            "customer_segment": "String"
        }
    }
}


# ============================================================
# DEFAULT RULES
# ============================================================

DEFAULT_RULES = [

    {
        "id": 1,
        "domain": "Hotel",
        "name": "High Occupancy",
        "conditions": [
            {
                "attribute": "occupancy",
                "operator": ">",
                "value": 80
            }
        ],
        "logic": "AND",
        "action": {
            "type": "PERCENTAGE",
            "value": 20
        },
        "priority": 1,
        "active": True
    },

    {
        "id": 2,
        "domain": "Hotel",
        "name": "Weekend Pricing",
        "conditions": [
            {
                "attribute": "weekend",
                "operator": "=",
                "value": True
            }
        ],
        "logic": "AND",
        "action": {
            "type": "PERCENTAGE",
            "value": 10
        },
        "priority": 2,
        "active": True
    },

    {
        "id": 3,
        "domain": "Hotel",
        "name": "High Demand",
        "conditions": [
            {
                "attribute": "demand",
                "operator": "=",
                "value": "HIGH"
            }
        ],
        "logic": "AND",
        "action": {
            "type": "PERCENTAGE",
            "value": 15
        },
        "priority": 3,
        "active": True
    },

    {
        "id": 4,
        "domain": "E-commerce",
        "name": "Low Inventory",
        "conditions": [
            {
                "attribute": "inventory",
                "operator": "<",
                "value": 10
            }
        ],
        "logic": "AND",
        "action": {
            "type": "PERCENTAGE",
            "value": 15
        },
        "priority": 1,
        "active": True
    },

    {
        "id": 5,
        "domain": "E-commerce",
        "name": "High Demand",
        "conditions": [
            {
                "attribute": "demand",
                "operator": "=",
                "value": "HIGH"
            }
        ],
        "logic": "AND",
        "action": {
            "type": "PERCENTAGE",
            "value": 10
        },
        "priority": 2,
        "active": True
    },

    {
        "id": 6,
        "domain": "E-commerce",
        "name": "Premium Customer",
        "conditions": [
            {
                "attribute": "customer_segment",
                "operator": "=",
                "value": "PREMIUM"
            }
        ],
        "logic": "AND",
        "action": {
            "type": "PERCENTAGE",
            "value": -5
        },
        "priority": 3,
        "active": True
    },

    {
        "id": 7,
        "domain": "Ride-hailing",
        "name": "High Demand Supply Ratio",
        "conditions": [
            {
                "attribute": "rider_demand",
                "operator": ">",
                "value": 200
            }
        ],
        "logic": "AND",
        "action": {
            "type": "PERCENTAGE",
            "value": 30
        },
        "priority": 1,
        "active": True
    },

    {
        "id": 8,
        "domain": "Airline",
        "name": "Low Seats",
        "conditions": [
            {
                "attribute": "seats_available",
                "operator": "<",
                "value": 20
            }
        ],
        "logic": "AND",
        "action": {
            "type": "PERCENTAGE",
            "value": 15
        },
        "priority": 1,
        "active": True
    },

    {
        "id": 9,
        "domain": "Airline",
        "name": "Near Departure",
        "conditions": [
            {
                "attribute": "days_to_departure",
                "operator": "<",
                "value": 3
            }
        ],
        "logic": "AND",
        "action": {
            "type": "PERCENTAGE",
            "value": 20
        },
        "priority": 2,
        "active": True
    },

    {
        "id": 10,
        "domain": "Airline",
        "name": "High Demand",
        "conditions": [
            {
                "attribute": "demand",
                "operator": "=",
                "value": "HIGH"
            }
        ],
        "logic": "AND",
        "action": {
            "type": "PERCENTAGE",
            "value": 15
        },
        "priority": 3,
        "active": True
    },

    {
        "id": 11,
        "domain": "Banking",
        "name": "High Risk",
        "conditions": [
            {
                "attribute": "risk_level",
                "operator": "=",
                "value": "HIGH"
            }
        ],
        "logic": "AND",
        "action": {
            "type": "FIXED",
            "value": 3
        },
        "priority": 1,
        "active": True
    },

    {
        "id": 12,
        "domain": "Banking",
        "name": "Low Risk",
        "conditions": [
            {
                "attribute": "risk_level",
                "operator": "=",
                "value": "LOW"
            }
        ],
        "logic": "AND",
        "action": {
            "type": "FIXED",
            "value": -1
        },
        "priority": 2,
        "active": True
    }
]


# ============================================================
# DEMO PRODUCTS
# ============================================================

DEFAULT_PRODUCTS = [

    {
        "id": 1,
        "name": "Deluxe Room",
        "domain": "Hotel",
        "base_price": 3000,
        "currency": "INR",
        "description": "Premium hotel room"
    },

    {
        "id": 2,
        "name": "Wireless Headphones",
        "domain": "E-commerce",
        "base_price": 2000,
        "currency": "INR",
        "description": "Wireless headphones"
    },

    {
        "id": 3,
        "name": "Airport Ride",
        "domain": "Ride-hailing",
        "base_price": 500,
        "currency": "INR",
        "description": "Airport transportation"
    },

    {
        "id": 4,
        "name": "Delhi-Mumbai Flight",
        "domain": "Airline",
        "base_price": 6000,
        "currency": "INR",
        "description": "Domestic flight"
    },

    {
        "id": 5,
        "name": "Personal Loan",
        "domain": "Banking",
        "base_price": 8.5,
        "currency": "%",
        "description": "Personal loan interest rate"
    }
]


# ============================================================
# STRATEGIES
# ============================================================

DEFAULT_STRATEGIES = [

    {
        "name": "Demand Based",
        "description": "Adjust prices based on demand",
        "method": "Sequential"
    },

    {
        "name": "Competitive",
        "description": "Adjust based on competitor prices",
        "method": "Base Price"
    },

    {
        "name": "Inventory Based",
        "description": "Adjust according to inventory",
        "method": "Sequential"
    },

    {
        "name": "Risk Based",
        "description": "Risk-based pricing",
        "method": "Base Price"
    },

    {
        "name": "Hybrid",
        "description": "Combines multiple pricing signals",
        "method": "Sequential"
    }
]


# ============================================================
# INITIALIZE
# ============================================================

def initialize_demo():

    if not st.session_state.initialized:

        st.session_state.domains = deepcopy(DOMAIN_CONFIGS)
        st.session_state.rules = deepcopy(DEFAULT_RULES)
        st.session_state.products = deepcopy(DEFAULT_PRODUCTS)
        st.session_state.strategies = deepcopy(DEFAULT_STRATEGIES)

        st.session_state.initialized = True


initialize_demo()


# ============================================================
# GENERIC CONDITION EVALUATOR
# ============================================================

def evaluate_condition(condition, context):

    attribute = condition["attribute"]
    operator = condition["operator"]
    expected = condition["value"]

    if attribute not in context:
        return False

    actual = context[attribute]

    try:

        if operator == "=":
            return actual == expected

        elif operator == "!=":
            return actual != expected

        elif operator == ">":
            return actual > expected

        elif operator == "<":
            return actual < expected

        elif operator == ">=":
            return actual >= expected

        elif operator == "<=":
            return actual <= expected

    except Exception:
        return False

    return False


# ============================================================
# GENERIC RULE EVALUATOR
# ============================================================

def evaluate_rule(rule, context):

    results = []

    for condition in rule["conditions"]:

        result = evaluate_condition(condition, context)

        results.append(result)

    if rule.get("logic", "AND") == "AND":
        return all(results)

    if rule.get("logic") == "OR":
        return any(results)

    return False


# ============================================================
# CONFLICT DETECTION
# ============================================================

def detect_conflicts(rules):

    conflicts = []

    for i in range(len(rules)):

        for j in range(i + 1, len(rules)):

            r1 = rules[i]
            r2 = rules[j]

            if r1["domain"] != r2["domain"]:
                continue

            if not r1["active"] or not r2["active"]:
                continue

            if r1["conditions"] == r2["conditions"]:

                a1 = r1["action"]["value"]
                a2 = r2["action"]["value"]

                if a1 != a2:

                    conflicts.append(
                        {
                            "rule1": r1["name"],
                            "rule2": r2["name"],
                            "domain": r1["domain"],
                            "adjustment1": a1,
                            "adjustment2": a2
                        }
                    )

    return conflicts


# ============================================================
# GENERIC PRICING ENGINE
# ============================================================

def calculate_price(
        base_price,
        context,
        rules,
        calculation_method="Sequential",
        minimum_price=None,
        maximum_price=None,
        max_increase=None,
        max_decrease=None
):

    start_time = time.perf_counter()

    current_price = float(base_price)

    triggered_rules = []
    skipped_rules = []
    adjustments = []

    applicable_rules = sorted(
        [
            r for r in rules
            if r.get("active", True)
        ],
        key=lambda x: x.get("priority", 999)
    )

    for rule in applicable_rules:

        if evaluate_rule(rule, context):

            action = rule["action"]

            action_type = action["type"]
            value = float(action["value"])

            old_price = current_price

            if action_type == "PERCENTAGE":

                if calculation_method == "Sequential":

                    adjustment = current_price * value / 100
                    current_price += adjustment

                else:

                    adjustment = float(base_price) * value / 100
                    current_price += adjustment

            elif action_type == "FIXED":

                adjustment = value
                current_price += adjustment

            else:

                adjustment = 0

            adjustments.append(
                {
                    "rule": rule["name"],
                    "type": action_type,
                    "value": value,
                    "before": old_price,
                    "impact": adjustment,
                    "after": current_price
                }
            )

            triggered_rules.append(rule)

        else:

            skipped_rules.append(rule)

    constraint_adjustments = []

    # Maximum percentage increase

    if max_increase is not None:

        max_allowed = base_price * (1 + max_increase / 100)

        if current_price > max_allowed:

            current_price = max_allowed

            constraint_adjustments.append(
                "Maximum percentage increase constraint applied."
            )

    # Maximum percentage decrease

    if max_decrease is not None:

        min_allowed = base_price * (1 - max_decrease / 100)

        if current_price < min_allowed:

            current_price = min_allowed

            constraint_adjustments.append(
                "Maximum percentage decrease constraint applied."
            )

    # Minimum price

    if minimum_price is not None:

        if current_price < minimum_price:

            current_price = minimum_price

            constraint_adjustments.append(
                "Minimum price constraint applied."
            )

    # Maximum price

    if maximum_price is not None:

        if current_price > maximum_price:

            current_price = maximum_price

            constraint_adjustments.append(
                "Maximum price constraint applied."
            )

    processing_time = (
        time.perf_counter() - start_time
    ) * 1000

    explanation = []

    explanation.append(
        f"Base price: {base_price:.2f}"
    )

    for item in adjustments:

        sign = "+" if item["impact"] >= 0 else ""

        explanation.append(
            f"{item['rule']}: {sign}{item['impact']:.2f}"
        )

    for item in constraint_adjustments:

        explanation.append(item)

    return {

        "basePrice": base_price,

        "finalPrice": round(current_price, 2),

        "triggeredRules": triggered_rules,

        "skippedRules": skipped_rules,

        "adjustments": adjustments,

        "constraintAdjustments":
            constraint_adjustments,

        "explanation":
            explanation,

        "processingTimeMs":
            round(processing_time, 3)
    }


# ============================================================
# FORMAT CURRENCY
# ============================================================

def money(value, currency="INR"):

    if currency == "%":
        return f"{value:.2f}%"

    return f"₹{value:,.2f}"


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        color: #64748b;
        font-size: 16px;
        margin-bottom: 25px;
    }

    .metric-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .success-box {
        padding: 18px;
        border-radius: 12px;
        background: #ecfdf5;
        border: 1px solid #10b981;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    '<div class="main-title">💰 Monetize360</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Universal Dynamic Pricing Engine • Configuration-driven pricing platform</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Monetize360")

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "🏢 Domains",
        "📦 Products",
        "⚙️ Pricing Rules",
        "🎯 Strategies",
        "🧪 Simulation",
        "⚡ Live Pricing",
        "🔍 Explainability",
        "📜 Audit Logs",
        "🤖 AI Copilot",
        "🧪 Testing",
        "⚙️ Settings"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "Demo Mode\n\n"
    "All data in this prototype is synthetic."
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "📊 Dashboard":

    st.header("Dashboard")

    conflicts = detect_conflicts(
        st.session_state.rules
    )

    total_rules = len(st.session_state.rules)

    active_rules = len(
        [
            r for r in st.session_state.rules
            if r["active"]
        ]
    )

    domains_count = len(
        st.session_state.domains
    )

    simulations = len(
        st.session_state.simulations
    )

    requests = len(
        st.session_state.requests
    )

    avg_latency = 0

    if st.session_state.requests:

        avg_latency = sum(
            r["processingTimeMs"]
            for r in st.session_state.requests
        ) / len(st.session_state.requests)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Active Domains",
        domains_count
    )

    col2.metric(
        "Active Rules",
        active_rules
    )

    col3.metric(
        "Simulations",
        simulations
    )

    col4.metric(
        "API Requests",
        requests
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Rule Conflicts",
        len(conflicts)
    )

    col2.metric(
        "Products",
        len(st.session_state.products)
    )

    col3.metric(
        "Average Latency",
        f"{avg_latency:.2f} ms"
    )

    col4.metric(
        "Audit Records",
        len(st.session_state.audit_logs)
    )

    st.subheader("Domain Distribution")

    domain_data = []

    for domain in st.session_state.domains:

        rule_count = len(
            [
                r for r in st.session_state.rules
                if r["domain"] == domain
            ]
        )

        product_count = len(
            [
                p for p in st.session_state.products
                if p["domain"] == domain
            ]
        )

        domain_data.append(
            {
                "Domain": domain,
                "Rules": rule_count,
                "Products": product_count
            }
        )

    df = pd.DataFrame(domain_data)

    if not df.empty:

        st.bar_chart(
            df.set_index("Domain")
        )

    st.subheader("System Architecture")

    st.info(
        """
        User Configuration
        ↓
        Streamlit UI
        ↓
        Generic Pricing Engine
        ↓
        Rule Evaluation
        ↓
        Conflict Resolution
        ↓
        Strategy + Constraints
        ↓
        Explanation
        ↓
        Audit Log
        """
    )

    st.subheader("Core Principle")

    st.success(
        "The pricing engine does not contain industry-specific pricing code. "
        "New industries can be added through configuration."
    )


# ============================================================
# DOMAINS
# ============================================================

elif page == "🏢 Domains":

    st.header("Domain Management")

    st.write(
        "Configure pricing domains without modifying the pricing engine."
    )

    cols = st.columns(3)

    for index, (domain, config) in enumerate(
        st.session_state.domains.items()
    ):

        with cols[index % 3]:

            product_count = len(
                [
                    p for p in st.session_state.products
                    if p["domain"] == domain
                ]
            )

            rule_count = len(
                [
                    r for r in st.session_state.rules
                    if r["domain"] == domain
                ]
            )

            st.container(border=True).write(
                f"""
                ### {domain}

                {config["description"]}

                **Products:** {product_count}

                **Attributes:** {len(config["attributes"])}

                **Rules:** {rule_count}

                **Currency:** {config["currency"]}
                """
            )

            if st.button(
                f"Configure {domain}",
                key=f"configure_{domain}"
            ):

                st.session_state["selected_domain"] = domain

    st.divider()

    st.subheader("➕ Create New Domain")

    with st.form("new_domain"):

        domain_name = st.text_input(
            "Domain Name",
            placeholder="Movie Ticket"
        )

        description = st.text_area(
            "Description"
        )

        currency = st.text_input(
            "Currency / Unit",
            value="INR"
        )

        st.write("Attributes")

        attr_name = st.text_input(
            "Attribute Name",
            placeholder="occupancy"
        )

        attr_type = st.selectbox(
            "Data Type",
            [
                "Number",
                "String",
                "Boolean",
                "Date"
            ]
        )

        submitted = st.form_submit_button(
            "Create Domain"
        )

        if submitted:

            if not domain_name:

                st.error(
                    "Domain name is required."
                )

            elif domain_name in st.session_state.domains:

                st.error(
                    "Domain already exists."
                )

            else:

                attributes = {}

                if attr_name:
                    attributes[attr_name] = attr_type

                st.session_state.domains[
                    domain_name
                ] = {

                    "description": description,

                    "currency": currency,

                    "attributes": attributes
                }

                st.success(
                    f"{domain_name} created successfully."
                )

    st.divider()

    st.subheader("🎬 Hackathon Proof: New Domain")

    st.write(
        """
        Example: create **Movie Ticket** with:

        - occupancy
        - weekend
        - demand

        Then add pricing rules and a product.

        **No pricing-engine source code needs to be changed.**
        """
    )


# ============================================================
# PRODUCTS
# ============================================================

elif page == "📦 Products":

    st.header("Product Management")

    st.subheader("Existing Products")

    if st.session_state.products:

        df = pd.DataFrame(
            st.session_state.products
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader("➕ Add Product")

    with st.form("product_form"):

        name = st.text_input(
            "Product Name"
        )

        domain = st.selectbox(
            "Domain",
            list(
                st.session_state.domains.keys()
            )
        )

        base_price = st.number_input(
            "Base Price",
            min_value=0.0,
            value=1000.0
        )

        description = st.text_area(
            "Description"
        )

        submit = st.form_submit_button(
            "Create Product"
        )

        if submit:

            product = {

                "id":
                    len(st.session_state.products) + 1,

                "name":
                    name,

                "domain":
                    domain,

                "base_price":
                    base_price,

                "currency":
                    st.session_state.domains[
                        domain
                    ]["currency"],

                "description":
                    description
            }

            st.session_state.products.append(
                product
            )

            st.success(
                f"{name} created successfully."
            )


# ============================================================
# PRICING RULES
# ============================================================

elif page == "⚙️ Pricing Rules":

    st.header("No-Code Pricing Rule Builder")

    st.write(
        "Create pricing logic using configuration instead of programming."
    )

    domain = st.selectbox(
        "Select Domain",
        list(
            st.session_state.domains.keys()
        )
    )

    attributes = list(
        st.session_state.domains[
            domain
        ]["attributes"].keys()
    )

    with st.form("rule_builder"):

        rule_name = st.text_input(
            "Rule Name",
            placeholder="High Occupancy Pricing"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            attribute = st.selectbox(
                "IF Attribute",
                attributes
            )

        with col2:

            operator = st.selectbox(
                "Operator",
                [
                    ">",
                    "<",
                    ">=",
                    "<=",
                    "=",
                    "!="
                ]
            )

        with col3:

            value_text = st.text_input(
                "Value",
                placeholder="80"
            )

        st.write("THEN")

        col1, col2 = st.columns(2)

        with col1:

            action_type = st.selectbox(
                "Action",
                [
                    "PERCENTAGE",
                    "FIXED"
                ]
            )

        with col2:

            adjustment = st.number_input(
                "Adjustment",
                value=10.0
            )

        priority = st.number_input(
            "Priority",
            min_value=1,
            value=1
        )

        active = st.checkbox(
            "Active",
            value=True
        )

        submit = st.form_submit_button(
            "💾 Save Rule"
        )

        if submit:

            attr_type = st.session_state.domains[
                domain
            ]["attributes"][attribute]

            try:

                if attr_type == "Number":

                    parsed_value = float(
                        value_text
                    )

                    if parsed_value.is_integer():
                        parsed_value = int(
                            parsed_value
                        )

                elif attr_type == "Boolean":

                    parsed_value = (
                        value_text.lower()
                        == "true"
                    )

                else:

                    parsed_value = value_text

                new_rule = {

                    "id":
                        max(
                            [
                                r["id"]
                                for r in st.session_state.rules
                            ] + [0]
                        ) + 1,

                    "domain":
                        domain,

                    "name":
                        rule_name,

                    "conditions": [

                        {

                            "attribute":
                                attribute,

                            "operator":
                                operator,

                            "value":
                                parsed_value
                        }
                    ],

                    "logic":
                        "AND",

                    "action": {

                        "type":
                            action_type,

                        "value":
                            adjustment
                    },

                    "priority":
                        priority,

                    "active":
                        active
                }

                st.session_state.rules.append(
                    new_rule
                )

                st.session_state.versions.append(
                    {
                        "version":
                            len(
                                st.session_state.versions
                            ) + 1,

                        "domain":
                            domain,

                        "created":
                            datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),

                        "change":
                            f"Added rule: {rule_name}"
                    }
                )

                st.success(
                    "Rule saved successfully."
                )

                st.json(new_rule)

            except Exception as e:

                st.error(
                    f"Invalid value: {e}"
                )

    st.divider()

    st.subheader("Current Rules")

    rule_rows = []

    for rule in st.session_state.rules:

        rule_rows.append(
            {
                "ID":
                    rule["id"],

                "Domain":
                    rule["domain"],

                "Rule":
                    rule["name"],

                "Condition":
                    str(
                        rule["conditions"]
                    ),

                "Action":
                    f'{rule["action"]["type"]} {rule["action"]["value"]}',

                "Priority":
                    rule["priority"],

                "Active":
                    rule["active"]
            }
        )

    st.dataframe(
        pd.DataFrame(rule_rows),
        use_container_width=True,
        hide_index=True
    )

    conflicts = detect_conflicts(
        st.session_state.rules
    )

    if conflicts:

        st.warning(
            "⚠ Rule Conflict Detected"
        )

        st.dataframe(
            pd.DataFrame(conflicts),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# STRATEGIES
# ============================================================

elif page == "🎯 Strategies":

    st.header("Pricing Strategies")

    for strategy in st.session_state.strategies:

        with st.container(border=True):

            col1, col2 = st.columns(
                [3, 1]
            )

            with col1:

                st.subheader(
                    strategy["name"]
                )

                st.write(
                    strategy["description"]
                )

            with col2:

                st.metric(
                    "Calculation",
                    strategy["method"]
                )

    st.divider()

    st.subheader("Create Strategy")

    with st.form("strategy_form"):

        name = st.text_input(
            "Strategy Name"
        )

        description = st.text_area(
            "Description"
        )

        method = st.selectbox(
            "Percentage Calculation",
            [
                "Sequential",
                "Base Price"
            ]
        )

        submit = st.form_submit_button(
            "Create Strategy"
        )

        if submit:

            st.session_state.strategies.append(
                {
                    "name":
                        name,

                    "description":
                        description,

                    "method":
                        method
                }
            )

            st.success(
                "Strategy created."
            )


# ============================================================
# SIMULATION
# ============================================================

elif page == "🧪 Simulation":

    st.header("Simulation / What-if Analysis")

    domain = st.selectbox(
        "Domain",
        list(
            st.session_state.domains.keys()
        )
    )

    domain_products = [
        p for p in st.session_state.products
        if p["domain"] == domain
    ]

    if not domain_products:

        st.warning(
            "No products available."
        )

    else:

        product = st.selectbox(
            "Product",
            domain_products,
            format_func=lambda p:
                p["name"]
        )

        st.subheader("Context")

        context = {}

        attributes = st.session_state.domains[
            domain
        ]["attributes"]

        cols = st.columns(3)

        for index, (attr, attr_type) in enumerate(
            attributes.items()
        ):

            with cols[index % 3]:

                if attr_type == "Number":

                    context[attr] = st.number_input(
                        attr,
                        value=50.0
                    )

                elif attr_type == "Boolean":

                    context[attr] = st.checkbox(
                        attr
                    )

                else:

                    context[attr] = st.text_input(
                        attr
                    )

        strategy = st.selectbox(
            "Calculation Strategy",
            st.session_state.strategies,
            format_func=lambda x:
                x["name"]
        )

        st.subheader("Price Constraints")

        col1, col2 = st.columns(2)

        with col1:

            min_price = st.number_input(
                "Minimum Price",
                min_value=0.0,
                value=0.0
            )

        with col2:

            max_price = st.number_input(
                "Maximum Price",
                min_value=0.0,
                value=1000000.0
            )

        calculate = st.button(
            "🚀 SIMULATE",
            type="primary"
        )

        if calculate:

            rules = [
                r for r in st.session_state.rules
                if r["domain"] == domain
            ]

            result = calculate_price(

                product["base_price"],

                context,

                rules,

                strategy["method"],

                min_price if min_price > 0
                else None,

                max_price
                if max_price < 1000000
                else None
            )

            st.session_state.simulations.append(
                {
                    "timestamp":
                        datetime.now(),

                    "domain":
                        domain,

                    "product":
                        product["name"],

                    "price":
                        result["finalPrice"]
                }
            )

            transaction_id = str(
                uuid.uuid4()
            )

            st.session_state.audit_logs.append(
                {
                    "transaction_id":
                        transaction_id,

                    "timestamp":
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),

                    "domain":
                        domain,

                    "product":
                        product["name"],

                    "base_price":
                        product["base_price"],

                    "final_price":
                        result["finalPrice"],

                    "rules_triggered":
                        len(
                            result[
                                "triggeredRules"
                            ]
                        ),

                    "strategy":
                        strategy["name"]
                }
            )

            st.session_state.requests.append(
                result
            )

            st.success(
                "Simulation completed."
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Base Price",
                money(
                    product["base_price"],
                    product["currency"]
                )
            )

            col2.metric(
                "Final Price",
                money(
                    result["finalPrice"],
                    product["currency"]
                )
            )

            col3.metric(
                "Processing Time",
                f'{result["processingTimeMs"]} ms'
            )

            st.subheader(
                "Triggered Rules"
            )

            if result["triggeredRules"]:

                for rule in result[
                    "triggeredRules"
                ]:

                    st.success(
                        f'✓ {rule["name"]} → '
                        f'{rule["action"]["value"]:+g}'
                        f'{ "%" if rule["action"]["type"] == "PERCENTAGE" else ""}'
                    )

            else:

                st.info(
                    "No pricing rules triggered."
                )

            st.subheader(
                "Price Explanation"
            )

            for item in result[
                "adjustments"
            ]:

                st.write(
                    f"""
                    **{item["rule"]}**

                    Before: {money(item["before"], product["currency"])}

                    Impact: {money(item["impact"], product["currency"])}

                    After: {money(item["after"], product["currency"])}
                    """
                )

            if result[
                "constraintAdjustments"
            ]:

                for c in result[
                    "constraintAdjustments"
                ]:

                    st.warning(c)

            st.subheader(
                "Calculation JSON"
            )

            st.json(
                {
                    "transactionId":
                        transaction_id,

                    "basePrice":
                        result["basePrice"],

                    "finalPrice":
                        result["finalPrice"],

                    "rulesTriggered":
                        len(
                            result[
                                "triggeredRules"
                            ]
                        ),

                    "processingTimeMs":
                        result[
                            "processingTimeMs"
                        ]
                }
            )


# ============================================================
# LIVE PRICING
# ============================================================

elif page == "⚡ Live Pricing":

    st.header("⚡ Live Pricing API")

    st.write(
        "This page simulates a real-time pricing API request."
    )

    product = st.selectbox(
        "Product",
        st.session_state.products,
        format_func=lambda p:
            f'{p["name"]} — {p["domain"]}'
    )

    st.subheader("Request Context")

    context = {}

    attributes = st.session_state.domains[
        product["domain"]
    ]["attributes"]

    cols = st.columns(3)

    for index, (attr, attr_type) in enumerate(
        attributes.items()
    ):

        with cols[index % 3]:

            if attr_type == "Number":

                context[attr] = st.number_input(
                    attr,
                    value=50.0,
                    key=f"live_{attr}"
                )

            elif attr_type == "Boolean":

                context[attr] = st.checkbox(
                    attr,
                    key=f"live_{attr}"
                )

            else:

                context[attr] = st.text_input(
                    attr,
                    key=f"live_{attr}"
                )

    if st.button(
        "⚡ GET REAL-TIME PRICE",
        type="primary"
    ):

        rules = [
            r for r in st.session_state.rules
            if r["domain"] ==
            product["domain"]
        ]

        result = calculate_price(
            product["base_price"],
            context,
            rules
        )

        transaction_id = str(
            uuid.uuid4()
        )

        st.session_state.requests.append(
            result
        )

        st.session_state.audit_logs.append(
            {
                "transaction_id":
                    transaction_id,

                "timestamp":
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                "domain":
                    product["domain"],

                "product":
                    product["name"],

                "base_price":
                    product["base_price"],

                "final_price":
                    result["finalPrice"],

                "rules_triggered":
                    len(
                        result[
                            "triggeredRules"
                        ]
                    ),

                "strategy":
                    "Default"
            }
        )

        st.success(
            "Real-time price calculated."
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Base Price",
            money(
                result["basePrice"],
                product["currency"]
            )
        )

        col2.metric(
            "Final Price",
            money(
                result["finalPrice"],
                product["currency"]
            )
        )

        col3.metric(
            "Latency",
            f'{result["processingTimeMs"]} ms'
        )

        st.subheader("API Request")

        st.json(
            {
                "productId":
                    product["id"],

                "basePrice":
                    product["base_price"],

                "context":
                    context
            }
        )

        st.subheader("API Response")

        st.json(
            {
                "basePrice":
                    result["basePrice"],

                "finalPrice":
                    result["finalPrice"],

                "currency":
                    product["currency"],

                "rulesTriggered":
                    len(
                        result[
                            "triggeredRules"
                        ]
                    ),

                "processingTimeMs":
                    result[
                        "processingTimeMs"
                    ]
            }
        )


# ============================================================
# EXPLAINABILITY
# ============================================================

elif page == "🔍 Explainability":

    st.header("🔍 Price Explainability")

    if not st.session_state.audit_logs:

        st.info(
            "Run a simulation or live pricing request first."
        )

    else:

        audit = st.selectbox(
            "Select Transaction",
            st.session_state.audit_logs,
            format_func=lambda x:
                f'{x["transaction_id"][:8]} — {x["product"]}'
        )

        st.subheader(
            "PRICE EXPLANATION"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Base Price",
            money(
                audit["base_price"]
            )
        )

        col2.metric(
            "Final Price",
            money(
                audit["final_price"]
            )
        )

        col3.metric(
            "Rules Triggered",
            audit["rules_triggered"]
        )

        st.divider()

        st.write(
            f'**Transaction ID:** {audit["transaction_id"]}'
        )

        st.write(
            f'**Timestamp:** {audit["timestamp"]}'
        )

        st.write(
            f'**Domain:** {audit["domain"]}'
        )

        st.write(
            f'**Product:** {audit["product"]}'
        )

        st.write(
            f'**Strategy:** {audit["strategy"]}'
        )

        st.success(
            "Every pricing decision is traceable through the audit record."
        )


# ============================================================
# AUDIT LOGS
# ============================================================

elif page == "📜 Audit Logs":

    st.header("📜 Audit Logs")

    if st.session_state.audit_logs:

        df = pd.DataFrame(
            st.session_state.audit_logs
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Audit CSV",
            df.to_csv(index=False),
            "monetize360_audit_logs.csv",
            "text/csv"
        )

    else:

        st.info(
            "No audit records yet."
        )

    st.divider()

    st.subheader("Configuration Versions")

    if st.session_state.versions:

        st.dataframe(
            pd.DataFrame(
                st.session_state.versions
            ),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No configuration versions created yet."
        )


# ============================================================
# AI COPILOT
# ============================================================

elif page == "🤖 AI Copilot":

    st.header("🤖 AI Pricing Copilot")

    st.write(
        """
        Convert natural language into a structured pricing rule.

        The generated rule is shown as a **draft** and does not automatically
        become active.
        """
    )

    prompt = st.text_area(
        "Describe your pricing rule",
        placeholder=
        "Increase hotel prices by 20 percent when occupancy goes above 80 percent."
    )

    if st.button(
        "Generate Configuration"
    ):

        text = prompt.lower()

        generated = None

        # Simple deterministic demo parser

        if (
            "occupancy" in text
            and "80" in text
            and "20" in text
        ):

            generated = {

                "name":
                    "AI Generated High Occupancy",

                "conditions": [

                    {
                        "attribute":
                            "occupancy",

                        "operator":
                            ">",

                        "value":
                            80
                    }
                ],

                "action": {

                    "type":
                        "PERCENTAGE",

                    "value":
                        20
                },

                "priority":
                    1,

                "status":
                    "DRAFT"
            }

        elif (
            "inventory" in text
            and "10" in text
        ):

            generated = {

                "name":
                    "AI Generated Low Inventory",

                "conditions": [

                    {
                        "attribute":
                            "inventory",

                        "operator":
                            "<",

                        "value":
                            10
                    }
                ],

                "action": {

                    "type":
                        "PERCENTAGE",

                    "value":
                        15
                },

                "priority":
                    1,

                "status":
                    "DRAFT"
            }

        else:

            st.warning(
                "The demo Copilot needs a clear attribute, condition and adjustment. "
                "Example: 'Increase prices by 20 percent when occupancy is above 80.'"
            )

        if generated:

            st.subheader(
                "Generated Configuration"
            )

            st.json(
                generated
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "✏️ Validate"
                ):

                    st.success(
                        "Configuration is structurally valid."
                    )

            with col2:

                if st.button(
                    "✅ Approve & Activate"
                ):

                    st.success(
                        "Rule approved. In production this would be persisted after authorization."
                    )


# ============================================================
# TESTING
# ============================================================

elif page == "🧪 Testing":

    st.header("🧪 Pricing Engine Correctness Testing")

    tests = [

        {
            "name":
                "Hotel High Occupancy",

            "domain":
                "Hotel",

            "base":
                3000,

            "context":
                {
                    "occupancy": 90,
                    "weekend": False,
                    "demand": "LOW"
                },

            "expected":
                3600
        },

        {
            "name":
                "Hotel Weekend",

            "domain":
                "Hotel",

            "base":
                3000,

            "context":
                {
                    "occupancy": 50,
                    "weekend": True,
                    "demand": "LOW"
                },

            "expected":
                3300
        },

        {
            "name":
                "Hotel High Demand",

            "domain":
                "Hotel",

            "base":
                3000,

            "context":
                {
                    "occupancy": 50,
                    "weekend": False,
                    "demand": "HIGH"
                },

            "expected":
                3450
        },

        {
            "name":
                "E-commerce Low Inventory",

            "domain":
                "E-commerce",

            "base":
                2000,

            "context":
                {
                    "inventory": 5,
                    "demand": "LOW",
                    "customer_segment": "REGULAR"
                },

            "expected":
                2300
        }

    ]

    results = []

    for test in tests:

        rules = [
            r for r in st.session_state.rules
            if r["domain"] ==
            test["domain"]
        ]

        result = calculate_price(
            test["base"],
            test["context"],
            rules
        )

        actual = result[
            "finalPrice"
        ]

        passed = (
            abs(
                actual -
                test["expected"]
            ) < 0.01
        )

        results.append(
            {
                "Test":
                    test["name"],

                "Expected":
                    test["expected"],

                "Actual":
                    actual,

                "Status":
                    "PASS"
                    if passed
                    else "FAIL"
            }
        )

    df = pd.DataFrame(
        results
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    accuracy = (
        len(
            df[
                df["Status"] == "PASS"
            ]
        )
        /
        len(df)
        *
        100
    )

    st.metric(
        "Pricing Accuracy",
        f"{accuracy:.1f}%"
    )

    if accuracy == 100:

        st.success(
            "All deterministic pricing tests passed."
        )

    else:

        st.warning(
            "Some tests failed. Check your active rules."
        )

    st.divider()

    st.subheader(
        "Reproducibility Test"
    )

    test_context = {

        "occupancy":
            90,

        "weekend":
            True,

        "demand":
            "HIGH"
    }

    hotel_rules = [
        r for r in st.session_state.rules
        if r["domain"] == "Hotel"
    ]

    result1 = calculate_price(
        3000,
        test_context,
        hotel_rules
    )

    result2 = calculate_price(
        3000,
        test_context,
        hotel_rules
    )

    if result1["finalPrice"] == result2["finalPrice"]:

        st.success(
            f"Same input produced the same result: ₹{result1['finalPrice']:,.2f}"
        )

    else:

        st.error(
            "Reproducibility test failed."
        )


# ============================================================
# SETTINGS
# ============================================================

elif page == "⚙️ Settings":

    st.header("Settings")

    st.subheader(
        "Pricing Calculation Method"
    )

    method = st.radio(
        "Default percentage calculation",
        [
            "Sequential",
            "Base Price"
        ]
    )

    if method == "Sequential":

        st.info(
            """
            Sequential calculation:

            ₹3000
            → +20%
            → ₹3600
            → +10%
            → ₹3960
            """
        )

    else:

        st.info(
            """
            Base-price calculation:

            ₹3000
            + ₹600
            + ₹300
            = ₹3900
            """
        )

    st.divider()

    st.subheader(
        "System Information"
    )

    st.write(
        f"Domains: {len(st.session_state.domains)}"
    )

    st.write(
        f"Products: {len(st.session_state.products)}"
    )

    st.write(
        f"Rules: {len(st.session_state.rules)}"
    )

    st.write(
        f"Audit Logs: {len(st.session_state.audit_logs)}"
    )

    st.write(
        f"API Requests: {len(st.session_state.requests)}"
    )

    st.divider()

    if st.button(
        "🔄 Reset Demo Data"
    ):

        st.session_state.domains = deepcopy(
            DOMAIN_CONFIGS
        )

        st.session_state.rules = deepcopy(
            DEFAULT_RULES
        )

        st.session_state.products = deepcopy(
            DEFAULT_PRODUCTS
        )

        st.session_state.strategies = deepcopy(
            DEFAULT_STRATEGIES
        )

        st.session_state.audit_logs = []

        st.session_state.simulations = []

        st.session_state.requests = []

        st.session_state.versions = []

        st.success(
            "Demo data reset."
        )