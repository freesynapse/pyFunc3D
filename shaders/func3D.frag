#version 330 core

layout (location=0) out vec4 frag_color;

in vec3 v_normal;
in vec3 v_frag_pos;
in vec3 v_barycentric;
in vec3 v_color;

uniform vec3 u_cam_pos;
uniform bool u_use_wireframe;
uniform bool u_use_lighting;
uniform vec3 u_Ipos;
// simple lighting constants
//const vec3 Ipos = vec3(2.5, 5, -2.5);
const vec3 Ia = vec3(1) * 0.2;
const vec3 Id = vec3(1) * 0.8;
const vec3 Is = vec3(1) * 0.3;

// wireframe rendering
const float line_width = 0.02;
const vec3 fill_color = vec3(0.9);
const vec3 stroke_color = vec3(0.0);

//
vec3 apply_lighting(vec3 color)
{
    vec3 normal = normalize(v_normal);

    // ambient component
    vec3 ambient = Ia;

    // diffuse component
    vec3 light_dir = normalize(u_Ipos - v_frag_pos);
    float diff = max(0, dot(light_dir, normal));
    vec3 diffuse = diff * Id;

    // specular component
    vec3 view_dir = normalize(u_cam_pos - v_frag_pos);
    vec3 reflect_dir = reflect(-light_dir, normal);
    float spec = pow(max(dot(view_dir, reflect_dir), 0), 16);
    vec3 specular = spec * Is;

    return color * (ambient + diffuse + specular);
}
//
float aastep(float threshold, float dist)
{
   float afwidth = fwidth(dist) * 0.5;
   return smoothstep(threshold - afwidth, threshold + afwidth, dist);
}
//
vec4 get_wireframe(vec3 barycentric, vec3 fill_color, vec3 stroke_color)
{
   // this will be our signed distance for the wireframe edge
   float d = min(min(barycentric.x, barycentric.y), barycentric.z);
   float edge = 1.0 - aastep(line_width, d);

   // now compute the final color of the mesh
   vec4 outColor = vec4(0.0);
   vec3 mainStroke = mix(fill_color, stroke_color, edge);
   //outColor.a = 0.6;
   outColor.a = 1.0;
   outColor.rgb = mainStroke;

   return outColor;
}
//
void main()
{
    vec3 fcolor;
    if (u_use_lighting)
        fcolor = apply_lighting(v_color);

    if (u_use_wireframe)
        frag_color = get_wireframe(v_barycentric, fcolor, stroke_color);
    else
        frag_color = vec4(fcolor, 1.0);

}

