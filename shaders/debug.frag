#version 330 core

layout (location=0) out vec4 frag_color;

in vec3 v_normal;

//
void main()
{
   frag_color = vec4(v_normal, 1.0);

}
