#version 330 core

layout (location=0) in vec3 a_position;
layout (location=1) in vec3 a_normal;
layout (location=2) in vec3 a_barycentric;
layout (location=3) in vec3 a_color;

out vec3 v_normal;
out vec3 v_frag_pos;
out vec3 v_barycentric;
out vec3 v_color;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

const vec3 barycentric_coords[6] = vec3[6](
    vec3(1, 0, 0), // even faces
    vec3(0, 1, 1), 
    vec3(0, 0, 1), 
    vec3(1, 0, 0), // odd faces
    vec3(1, 1, 0), 
    vec3(0, 0, 1)
);

void main()
{
    v_normal = mat3(transpose(inverse(m_model))) * normalize(a_normal);
    v_frag_pos = vec3(m_model * vec4(a_position, 1.0));
    v_barycentric = a_barycentric;
    v_color = a_color;
    
    gl_Position = m_proj * m_view * m_model * vec4(a_position, 1.0);

}


