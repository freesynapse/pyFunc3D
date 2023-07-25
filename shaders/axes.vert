#version 330 core

layout (location=0) in vec3 a_position;
layout (location=1) in float a_color_index;

out vec3 v_color;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

const vec3 colors[3] = vec3[3](
    vec3(0.7, 0.0, 0.0),
    vec3(0.0, 0.7, 0.0),
    vec3(0.0, 0.0, 0.7)
);

void main()
{
    v_color = colors[int(a_color_index)];
    gl_Position = m_proj * m_view * m_model * vec4(a_position, 1.0);

}
