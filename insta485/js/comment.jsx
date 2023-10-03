import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

export default function Comment({ url, comments }) {
    /* Update a comment */
    function handleSubmit(e) {
      // prevent the page from reloading
      e.preventDefault();
    };

    return (
      <div>
        {comments}
        <form data-testid="comment-form" onSubmit={handleSubmit}>
          <input type="text" value=""/>
          
        </form>
      </div>
    );
  }
  
  Comment.propTypes = {
    url: PropTypes.string.isRequired,
  };
  