import os
from openai import OpenAI
import json

if len(os.environ.get("GROQ_API_KEY")) > 30:
    from groq import Groq
#     model = "mixtral-8x7b-32768"
    model = "llama-3.3-70b-versatile"
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
        )
else:
    OPENAI_API_KEY = os.getenv('OPENAI_KEY')
    model = "gpt-4o"
    client = OpenAI(api_key=OPENAI_API_KEY)

def generate_script(topic):
    prompt = (
        """You are a seasoned content writer for a YouTube educational channel, specializing in educational videos. 
        Your content scripts have 600 words. They are incredibly engaging and original. When a user requests a specific type of content script, you will create it.
        They all consist of a welcome and introduction, chapters, and a conclusion.

        For instance, if the user asks for:
        Sugar
        You would produce content like this:

        - Welcome, everyone! Today, we’re talking about something that affects nearly every diet in the modern world — sugar. It’s in our drinks, snacks, sauces, cereals, and even in foods you wouldn’t expect, like bread or salad dressing. While sugar is a natural part of many foods and life itself, the growing concern is how much added sugar we consume and how it impacts our health. In this session, we’ll break down what sugar is, where it’s hiding, how much is too much, and how it affects your body. We’ll also cover practical tips to reduce sugar in a sustainable and healthy way.
        - Chapter 1: What Exactly Is Sugar?. Sugar is a simple carbohydrate, and it's one of the body’s main sources of energy. Natural sugars are found in fruits, milk, and vegetables, and these come packaged with fiber, vitamins, and minerals, which makes them a healthier choice. The problem arises with added sugars, which are introduced during food processing or preparation. These include substances like white sugar, high-fructose corn syrup, and various sweetening syrups. Added sugars provide calories but no significant nutritional benefits, earning them the label of “empty calories.” They are often found in soft drinks, baked goods, candy, sauces, and even seemingly healthy snacks.
        - Chapter 2: How Much Sugar Do We Actually Eat?. Health organizations like the World Health Organization recommend that added sugars make up less than 10% of daily caloric intake, with an ideal target of below 5%. That’s around 25 to 36 grams per day for the average adult, or roughly 6 to 9 teaspoons. Unfortunately, studies show that many people are consuming far more than this — often over 50 grams a day, and sometimes even double that. This is largely due to the widespread presence of sugar in processed foods and drinks, including some products marketed as healthy. Even a single can of soda can exceed the recommended daily limit, and added sugar in cereals, flavored yogurts, and snack bars quickly adds up throughout the day.
        - Chapter 3: Health Effects of Too Much Sugar. Overconsumption of sugar is linked to a wide range of health issues. One of the most common consequences is weight gain, especially when sugary foods are consumed regularly without balancing them with physical activity. Excess sugar is also strongly associated with type 2 diabetes, as it can lead to insulin resistance over time. High sugar intake has been shown to increase the risk of heart disease, even in people who are not overweight. In addition to chronic diseases, sugar can also cause immediate effects such as energy spikes followed by crashes, mood swings, and difficulty focusing. It contributes to tooth decay and poor dental health, and in children, high sugar diets are often linked to hyperactivity and disrupted sleep.
        - Chapter 4: How to Reduce Sugar Intake. The good news is that reducing sugar is entirely possible with a few conscious habits. The first step is becoming aware of how much sugar is in the foods you regularly eat by reading nutrition labels carefully. Avoiding sugary beverages is one of the easiest and most impactful changes you can make, since they often contain large amounts of added sugar with no nutritional benefit. Choosing whole fruits instead of fruit juices or sugary snacks is another great strategy. Preparing more meals at home gives you control over what goes into your food, making it easier to limit sugar. If you need something sweet, consider natural options like dates or small amounts of honey, but remember that even natural sugars should be used in moderation.
        - In conclusion, sugar is not inherently bad — in fact, it plays a role in providing energy and enjoyment. The key is moderation and awareness. By understanding where added sugar hides and how it affects our bodies, we can make smarter choices that protect our long-term health. Making small adjustments to your eating habits can lead to big improvements over time. You don’t have to eliminate sweetness from your life, but you can learn to enjoy it in healthier ways. Thank you for listening, and here’s to making informed, balanced, and healthier decisions about sugar.

        You are now tasked with creating the content script based on the user's requested topic.

        Keep it highly interesting, and unique.

        It is very important NOT to include any line breaks in the json. Each chapter should start with a dash and a space, and end with a dot.
        Do not add a line break between each chapter.
        Make chapters related and following the same line of thought, sequentially telling a compelling story.

        Strictly output the script in a JSON format like below, and only provide a parsable JSON object with the key 'script'.

        # Output
        {"script": "Here is the script ..."}
        """
    )

    response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": topic}
            ]
        )
    content = response.choices[0].message.content
    try:
        script = json.loads(content)["script"]
    except Exception as e:
        json_start_index = content.find('{')
        json_end_index = content.rfind('}')
        print(content)
        content = content[json_start_index:json_end_index+1]
        script = json.loads(content)["script"]
    return script
