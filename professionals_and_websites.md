---
title: "Professionels et Sites Web"
layout: page
---

{% assign categories = site.data.professionals_and_websites | sort %}

<div style="display: flex; flex-wrap: wrap; gap: 2rem;">

  {% for category in categories %}
    <div style="flex: 1 1 300px; min-width: 300px;">
      <h2>{{ category[0] }}</h2>
      <ul>
        {% assign entries = category[1] | sort: "title" %}
        {% for entry in entries %}
          <li>
            <strong>{{ entry.title }}</strong><br>
            {{ entry.description }}
          </li>
        {% endfor %}
      </ul>
    </div>
  {% endfor %}

</div>