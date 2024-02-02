use axum::{
    extract::Query,
    response::{Response, IntoResponse},
    http::{StatusCode, header},
    routing::get,
    Router,
    body::Body,
    async_trait,
};

use serde::Deserialize;
use std::collections::HashMap;
use ammonia::clean;


#[derive(Deserialize)]
pub struct TextParams {
    pub text: String,
    pub bg_l: Option<String>,
    pub bg_m: Option<String>,
    pub bg_r: Option<String>,
}


pub async fn jedi_controller(Query(params): Query<TextParams>) -> impl IntoResponse {

    let sanitized_text = clean(&params.text);

    let default_bg_l = "#800080";
    let default_bg_m = "#FFA500";
    let default_bg_r = "#FFC0CB";

    let _sanitized_bg_l = params.bg_l.as_ref().map_or(default_bg_l.to_string(), |color| clean(color));
    let _sanitized_bg_m = params.bg_m.as_ref().map_or(default_bg_m.to_string(), |color| clean(color));
    let _sanitized_bg_r = params.bg_r.as_ref().map_or(default_bg_r.to_string(), |color| clean(color));



    let svg_data = format!(
         sanitized_text
    );

    let svg_body = Body::from(svg_data);

    // Create a response with the SVG data and correct headers
    let response = Response::builder()
        .status(StatusCode::OK)
        .header(header::CONTENT_TYPE, "image/svg+xml")
        .body(svg_body)
        .unwrap();

    response
}