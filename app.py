import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from langchain.agents import create_agent
#from langchain_core.tools import Tool
from langchain_core.tools import tool
import math

st.set_page_config(page_title="Text To MAth Problem Solver And Data Serach Assistant",page_icon="🧮")
st.title("Text To Math Problem Solver Uing llama-3.1-8b-instant")

api_key = st.sidebar.text_input("Enter groq api key here",type="password")

if not api_key:
    st.error("Enetr api key to proceed")
    st.stop()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    groq_api_key=api_key
)

wikiWrapper = WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=2000)
wiki = WikipediaQueryRun(api_wrapper=wikiWrapper)

@tool
def calculator(expression: str) -> str:
    """Use this tool to perform ANY mathematical calculation.
This includes arithmetic, word problems, totals, counting, and numerical reasoning.
Always use this tool when numbers are involved."""
    try:
        allowed_names = {
            k: getattr(math, k) for k in dir(math) if not k.startswith("_")
        }
        allowed_names.update({
            "abs": abs,
            "round": round
        })

        result = eval(query, {"__builtins__": {}}, allowed_names)
        return str(result)

    except Exception as e:
        return f"Error: {str(e)}"

prompt_template="""
You are an agent tasked for solving users mathemtical question. Logically arrive at the solution and provide a detailed explanation
and display it point wise for the question below
Question:{question}
Answer:
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system",prompt_template),
        ("user","{question}")
    ]
)

chain = prompt|llm

# def reasoning_func(query: str):
#     return chain.invoke({"question": query}).content

# reasoning_tool = Tool(
#     name="LogicSolver",
#     func=reasoning_func,
#     description="Use ONLY for complex word problems requiring explanation. Do NOT use for direct calculations."
# )

agent = create_agent(llm,[calculator],system_prompt = """
You are a math assistant.

Rules:
- ALWAYS use the calculator tool when solving any math or numerical problem.
- For word problems, first convert to mathematical steps, then use the calculator.
- Do NOT answer math questions without using the calculator tool.
- Use Wikipedia only for factual queries.

Return final answer clearly.
""")

if "messages" not in st.session_state:
    st.session_state["messages"]=[
        {"role":"assistant","content":"Hi, I'm a MAth chatbot who can answer all your maths questions"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

question=st.text_area("Enter youe question:","I have 5 bananas and 7 grapes. I eat 2 bananas and give away 3 grapes. Then I buy a dozen apples and 2 packs of blueberries. Each pack of blueberries contains 25 berries. How many total pieces of fruit do I have at the end?")



if st.button("Answer"):
    if question:
        with st.spinner("Generating response.."):
            st.session_state.messages.append({"role":"user","content":question})
            st.chat_message("user").write(question)
            response = agent.invoke({"input": question})
            output = response["messages"][-1].content

            st.session_state.messages.append({
                "role": "assistant",
                "content": output
            })

            st.write(output)

            with st.expander("🧠 How I got this answer"):
                for msg in response["messages"]:
                    st.write(msg)








